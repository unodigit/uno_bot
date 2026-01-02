"""Google Calendar integration service for appointment booking."""
import asyncio
import datetime
from datetime import datetime, timedelta
from typing import List, Optional

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.core.config import settings


class CalendarService:
    """Service for managing Google Calendar integration and availability."""

    SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ]

    def __init__(self):
        self.google_client_id = settings.google_client_id
        self.google_client_secret = settings.google_client_secret
        self.google_redirect_uri = settings.google_redirect_uri

    def create_oauth_flow(self) -> InstalledAppFlow:
        """Create OAuth2 flow for expert authentication."""
        # For testing and development, create a mock OAuth flow that simulates Google OAuth
        # In production, this would use actual Google credentials
        if settings.environment in ["test", "development"]:
            # Return a mock flow for testing and development
            from unittest.mock import Mock

            mock_flow = Mock()
            mock_flow.authorization_url.return_value = (
                "https://test-oauth.example.com/auth", "test_state"
            )
            mock_flow.fetch_token = Mock()
            mock_flow.credentials = Mock()
            mock_flow.credentials.refresh_token = "test_refresh_token"
            mock_flow.credentials.client_id = "test_client_id"
            return mock_flow

        # Production flow
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json',  # This should be the path to OAuth credentials
            scopes=self.SCOPES,
            redirect_uri=self.google_redirect_uri
        )
        return flow

    def get_credentials_from_token(self, refresh_token: str) -> Credentials:
        """Get Google credentials from stored refresh token."""
        try:
            creds = Credentials(
                None,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.google_client_id,
                client_secret=self.google_client_secret
            )

            # Refresh the token
            creds.refresh(Request())
            return creds
        except RefreshError as e:
            print(f"Error refreshing credentials: {e}")
            raise Exception(f"Invalid refresh token: {e}")

    def get_calendar_service(self, refresh_token: str):
        """Get authenticated Google Calendar service."""
        creds = self.get_credentials_from_token(refresh_token)
        return build('calendar', 'v3', credentials=creds)

    async def get_expert_availability(
        self,
        refresh_token: str,
        timezone: str = 'UTC',
        days_ahead: int = 14,
        min_slots_to_show: int = 5
    ) -> List[dict]:
        """Get available time slots for an expert.

        Args:
            refresh_token: Expert's Google OAuth refresh token
            timezone: Expert's timezone
            days_ahead: Number of days to look ahead for availability
            min_slots_to_show: Minimum number of slots to return

        Returns:
            List of available time slots with start/end times
        """
        # For testing and development, return mock data
        if settings.environment in ["test", "development"]:
            return await self._get_mock_availability(timezone, days_ahead, min_slots_to_show)

        try:
            service = self.get_calendar_service(refresh_token)

            # Get current time in expert's timezone
            now = datetime.now()
            start_date = now.replace(
                hour=9, minute=0, second=0, microsecond=0
            )  # Start from 9 AM today
            end_date = start_date + timedelta(days=days_ahead)

            # Get calendar events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            # Define business hours (configurable per expert in future)
            business_start_hour = 9
            business_end_hour = 17

            available_slots = []
            current_time = start_date

            while len(available_slots) < min_slots_to_show and current_time < end_date:
                # Skip weekends
                if current_time.weekday() >= 5:  # Saturday=5, Sunday=6
                    current_time += timedelta(hours=24)
                    continue

                # Check business hours
                if current_time.hour < business_start_hour:
                    current_time = current_time.replace(
                        hour=business_start_hour, minute=0, second=0, microsecond=0
                    )
                    continue
                elif current_time.hour >= business_end_hour:
                    # Move to next day
                    current_time = current_time.replace(
                        hour=business_start_hour, minute=0, second=0, microsecond=0
                    ) + timedelta(days=1)
                    continue

                # Check if this time slot is available
                if self._is_time_slot_available(current_time, events):
                    # Add 1-hour slot
                    slot_end = current_time + timedelta(hours=1)
                    available_slots.append({
                        'start': current_time.isoformat(),
                        'end': slot_end.isoformat(),
                        'start_formatted': current_time.strftime('%Y-%m-%d %H:%M'),
                        'date': current_time.strftime('%Y-%m-%d'),
                        'time': current_time.strftime('%H:%M'),
                        'timezone': timezone
                    })

                # Move to next 30-minute slot
                current_time += timedelta(minutes=30)

            return available_slots

        except HttpError as e:
            print(f"Google Calendar API error: {e}")
            raise Exception(f"Failed to get availability: {e}")
        except Exception as e:
            print(f"Error getting availability: {e}")
            raise Exception(f"Failed to get availability: {e}")

    def _is_time_slot_available(
        self,
        start_time: datetime,
        events: List[dict]
    ) -> bool:
        """Check if a time slot is available (no conflicting events)."""
        end_time = start_time + timedelta(hours=1)
        buffer_minutes = settings.booking_buffer_minutes

        for event in events:
            event_start = datetime.fromisoformat(
                event['start']['dateTime'].replace('Z', '+00:00')
            )
            event_end = datetime.fromisoformat(
                event['end']['dateTime'].replace('Z', '+00:00')
            )

            # Check for conflicts with buffer time
            slot_start_with_buffer = start_time - timedelta(minutes=buffer_minutes)
            slot_end_with_buffer = end_time + timedelta(minutes=buffer_minutes)

            # Check if slots overlap
            if (slot_start_with_buffer < event_end and slot_end_with_buffer > event_start):
                return False

        return True

    async def create_calendar_event(
        self,
        refresh_token: str,
        expert_email: str,
        client_name: str,
        client_email: str,
        start_time: datetime,
        end_time: datetime,
        timezone: str = 'UTC'
    ) -> str:
        """Create a calendar event for the appointment.

        Args:
            refresh_token: Expert's Google OAuth refresh token
            expert_email: Expert's email address
            client_name: Client's name
            client_email: Client's email address
            start_time: Event start time
            end_time: Event end time
            timezone: Timezone for the event

        Returns:
            Event ID of the created calendar event
        """
        # For testing and development, return mock event ID
        if settings.environment in ["test", "development"]:
            import random
            return f"mock-event-{random.randint(10000, 99999)}"

        try:
            service = self.get_calendar_service(refresh_token)

            event = {
                'summary': f'UnoDigit Consultation with {client_name}',
                'description': f'Business consultation appointment generated through UnoBot.',
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': timezone,
                },
                'attendees': [
                    {'email': expert_email},
                    {'email': client_email},
                ],
                'conferenceData': {
                    'createRequest': {
                        'requestId': f'unobot-{int(start_time.timestamp())}',
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'email', 'minutes': 60},       # 1 hour before
                    ],
                },
            }

            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1
            ).execute()

            return created_event.get('id')

        except HttpError as e:
            print(f"Google Calendar API error: {e}")
            raise Exception(f"Failed to create calendar event: {e}")
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            raise Exception(f"Failed to create calendar event: {e}")

    async def get_calendar_timezone(self, refresh_token: str) -> str:
        """Get the expert's calendar timezone."""
        try:
            service = self.get_calendar_service(refresh_token)
            calendar = service.calendars().get(calendarId='primary').execute()
            return calendar.get('timeZone', 'UTC')
        except Exception as e:
            print(f"Error getting calendar timezone: {e}")
            return 'UTC'

    def format_time_slot(self, start_time: datetime, timezone: str) -> dict:
        """Format a time slot for display."""
        return {
            'start': start_time.isoformat(),
            'end': (start_time + timedelta(hours=1)).isoformat(),
            'start_formatted': start_time.strftime('%Y-%m-%d %H:%M'),
            'date': start_time.strftime('%Y-%m-%d'),
            'time': start_time.strftime('%H:%M'),
            'timezone': timezone
        }

    async def _get_mock_availability(
        self,
        timezone: str = 'UTC',
        days_ahead: int = 14,
        min_slots_to_show: int = 5
    ) -> List[dict]:
        """Generate mock availability for testing and development.

        Args:
            timezone: Timezone for the mock slots (e.g., 'America/New_York', 'Europe/London')
            days_ahead: Number of days to generate mock slots for
            min_slots_to_show: Minimum number of slots to return

        Returns:
            List of mock time slots with times in the requested timezone
        """
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo

        # Generate mock time slots for business days only
        slots = []

        # Use the requested timezone for generating slots
        # This simulates the expert's availability in the visitor's timezone
        try:
            tz_info = ZoneInfo(timezone)
        except Exception:
            # Fallback to UTC if timezone is invalid
            tz_info = ZoneInfo('UTC')

        # Get current time in the target timezone
        now = datetime.now(tz_info)

        for i in range(days_ahead):
            date = now + timedelta(days=i)
            if date.weekday() < 5:  # Only weekdays (Monday=0 to Friday=4)
                # Generate slots for business hours: 9 AM to 5 PM in the target timezone
                for hour in [9, 10, 11, 14, 15, 16]:  # Morning and afternoon slots
                    slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    # Convert to UTC for storage (ISO format with timezone info)
                    slot_time_utc = slot_time.astimezone(ZoneInfo('UTC'))
                    slot_end_utc = (slot_time + timedelta(hours=1)).astimezone(ZoneInfo('UTC'))

                    slots.append({
                        'start': slot_time_utc.isoformat(),
                        'end': slot_end_utc.isoformat(),
                        'start_formatted': slot_time.strftime('%Y-%m-%d %H:%M'),
                        'date': slot_time.strftime('%Y-%m-%d'),
                        'time': slot_time.strftime('%H:%M'),
                        'timezone': timezone
                    })

        # Return first N slots deterministically (not random) for consistent test behavior
        # This ensures the same slots are returned on subsequent calls
        available_slots = slots[:min_slots_to_show]

        return available_slots