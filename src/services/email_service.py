"""Email notification service using SendGrid for booking confirmations and reminders."""
import base64
from datetime import datetime

from src.core.config import settings


class EmailService:
    """Service for sending email notifications."""

    def __init__(self) -> None:
        self.api_key = settings.sendgrid_api_key
        self.from_email = settings.sendgrid_from_email
        self.environment = settings.environment

    async def send_booking_confirmation(
        self,
        client_email: str,
        client_name: str,
        expert_name: str,
        expert_role: str,
        start_time: datetime,
        end_time: datetime,
        timezone: str,
        meeting_link: str | None = None,
        prd_url: str | None = None,
        booking_id: str | None = None,
        session_id: str | None = None,
    ) -> bool:
        """Send booking confirmation email to client.

        Args:
            client_email: Client's email address
            client_name: Client's name
            expert_name: Expert's name
            expert_role: Expert's role
            start_time: Booking start time
            end_time: Booking end time
            timezone: Timezone for the booking
            meeting_link: Google Meet link (optional)
            prd_url: PRD document URL (optional)
            booking_id: Booking ID (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"✅ Booking Confirmed - Consultation with {expert_name}"

        # Format date and time
        date_str = start_time.strftime('%A, %B %d, %Y')
        start_time_str = start_time.strftime('%I:%M %p')
        end_time_str = end_time.strftime('%I:%M %p')

        # Build email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #2563EB, #1D4ED8); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">Booking Confirmed! 🎉</h1>
                </div>

                <!-- Content -->
                <div style="padding: 30px; background: #f9fafb; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px;">
                    <p style="margin: 0 0 20px 0;">Hi {client_name},</p>

                    <p style="margin: 0 0 20px 0;">Your consultation appointment has been confirmed with:</p>

                    <!-- Expert Card -->
                    <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb; margin-bottom: 20px;">
                        <div style="font-weight: bold; font-size: 16px; color: #111827; margin-bottom: 5px;">{expert_name}</div>
                        <div style="color: #6b7280; font-size: 14px; margin-bottom: 10px;">{expert_role}</div>

                        <div style="background: #eff6ff; padding: 10px; border-radius: 4px; margin-top: 10px;">
                            <div style="font-weight: 600; color: #1e40af; margin-bottom: 5px;">📅 {date_str}</div>
                            <div style="color: #1e40af;">⏰ {start_time_str} - {end_time_str} ({timezone})</div>
                        </div>
                    </div>
        """

        if meeting_link:
            body += f"""
                    <!-- Meeting Link -->
                    <div style="margin: 20px 0;">
                        <p style="margin: 0 0 10px 0; font-weight: 600;">Join the meeting:</p>
                        <a href="{meeting_link}" style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600;">Join Meeting</a>
                        <p style="margin: 10px 0 0 0; font-size: 12px; color: #6b7280;">Link: {meeting_link}</p>
                    </div>
            """

        if prd_url:
            body += f"""
                    <!-- PRD Document -->
                    <div style="margin: 20px 0;">
                        <p style="margin: 0 0 10px 0; font-weight: 600;">Project Requirements Document:</p>
                        <a href="{prd_url}" style="display: inline-block; background: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600;">Download PRD</a>
                    </div>
            """

        body += f"""
                    <!-- What's Next -->
                    <div style="margin: 20px 0; padding: 15px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px;">
                        <p style="margin: 0 0 10px 0; font-weight: 600; color: #166534;">What's Next?</p>
                        <ul style="margin: 0; padding-left: 20px; color: #166534; font-size: 14px;">
                            <li style="margin-bottom: 5px;">A calendar invite (.ics) is attached to this email</li>
                            <li style="margin-bottom: 5px;">You'll receive a reminder 24 hours before</li>
                            <li style="margin-bottom: 5px;">You'll receive a reminder 1 hour before</li>
                            <li>Join the meeting using the link above</li>
                        </ul>
                    </div>

                    <!-- Session Resume Link -->
                    {f'''
                    <div style="margin: 20px 0; padding: 15px; background: #fff7ed; border: 1px solid #fdba74; border-radius: 6px;">
                        <p style="margin: 0 0 10px 0; font-weight: 600; color: #c2410c;">Continue Your Conversation</p>
                        <p style="margin: 0 0 10px 0; color: #c2410c; font-size: 14px;">
                            If you need to continue our conversation or access your Project Requirements Document,
                        </p>
                        <a href="https://your-domain.com?session_id={session_id}" style="display: inline-block; background: #c2410c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600;">Resume Chat Session</a>
                    </div>
                    ''' if session_id else ''}

                    <!-- Footer -->
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                        <p style="margin: 0;">UnoBot - AI Business Consultant</p>
                        <p style="margin: 5px 0 0 0;">Powered by UnoDigit</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # In development/test mode, log the email instead of sending
        if self.environment in ["test", "development"]:
            print(f"\n{'='*60}")
            print("EMAIL NOTIFICATION (Development Mode)")
            print(f"{'='*60}")
            print(f"To: {client_email}")
            print(f"Subject: {subject}")
            print(f"Body Preview: {body[:500]}...")
            print(f"{'='*60}\n")
            return True

        # Production: Send via SendGrid
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Attachment, Mail

            # Create email message
            message = Mail(
                from_email=self.from_email,
                to_emails=client_email,
                subject=subject,
                html_content=body
            )

            # Add ICS calendar attachment if we have booking details
            if start_time and end_time and booking_id:
                ics_content = self._generate_ics_file(
                    summary=f"UnoDigit Consultation with {expert_name}",
                    description=f"Business consultation appointment with {expert_name}, {expert_role}",
                    start_time=start_time,
                    end_time=end_time,
                    timezone=timezone,
                    location=meeting_link or "To be determined",
                    uid=booking_id
                )

                attachment = Attachment(
                    file_content=base64.b64encode(ics_content.encode()).decode(),
                    file_name="appointment.ics",
                    file_type="text/calendar",
                    disposition="attachment"
                )
                message.attachment = attachment

            # Send email
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            return int(response.status_code) == 202

        except ImportError:
            print("SendGrid not installed. Install with: pip install sendgrid")
            return False
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    async def send_reminder_email(
        self,
        client_email: str,
        client_name: str,
        expert_name: str,
        start_time: datetime,
        end_time: datetime,
        timezone: str,
        meeting_link: str | None = None,
        hours_before: int = 24,
    ) -> bool:
        """Send reminder email before appointment.

        Args:
            client_email: Client's email address
            client_name: Client's name
            expert_name: Expert's name
            start_time: Booking start time
            end_time: Booking end time
            timezone: Timezone for the booking
            meeting_link: Google Meet link (optional)
            hours_before: Hours before appointment (24 or 1)

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"⏰ Reminder: Consultation with {expert_name} in {hours_before} hours"

        # Format date and time
        date_str = start_time.strftime('%A, %B %d, %Y')
        start_time_str = start_time.strftime('%I:%M %p')

        # Build email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #fef3c7; color: #92400e; padding: 20px; text-align: center; border-radius: 8px; border: 1px solid #fcd34d;">
                    <h2 style="margin: 0; font-size: 20px;">⏰ Upcoming Appointment Reminder</h2>
                </div>

                <div style="padding: 20px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 8px; margin-top: 15px;">
                    <p style="margin: 0 0 15px 0;">Hi {client_name},</p>

                    <p style="margin: 0 0 15px 0; font-size: 16px;">
                        This is a friendly reminder that you have a consultation with <strong>{expert_name}</strong>
                        <strong>{hours_before} hours</strong> from now.
                    </p>

                    <div style="background: #f9fafb; padding: 15px; border-radius: 6px; margin: 15px 0;">
                        <div style="font-weight: 600; margin-bottom: 8px;">📅 {date_str}</div>
                        <div style="color: #374151;">⏰ {start_time_str} ({timezone})</div>
                    </div>
        """

        if meeting_link:
            body += f"""
                    <div style="margin: 15px 0;">
                        <a href="{meeting_link}" style="display: inline-block; background: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: 600;">Join Meeting</a>
                    </div>
            """

        body += """
                    <p style="margin: 15px 0 0 0; font-size: 14px; color: #6b7280;">
                        If you need to reschedule or cancel, please contact us as soon as possible.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        # In development/test mode, log the email
        if self.environment in ["test", "development"]:
            print(f"\n{'='*60}")
            print(f"REMINDER EMAIL ({hours_before}h before) - Development Mode")
            print(f"{'='*60}")
            print(f"To: {client_email}")
            print(f"Subject: {subject}")
            print(f"{'='*60}\n")
            return True

        # Production: Send via SendGrid
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=self.from_email,
                to_emails=client_email,
                subject=subject,
                html_content=body
            )

            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            return int(response.status_code) == 202

        except ImportError:
            print("SendGrid not installed. Install with: pip install sendgrid")
            return False
        except Exception as e:
            print(f"Error sending reminder email: {e}")
            return False

    def _generate_ics_file(
        self,
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        timezone: str,
        location: str,
        uid: str,
    ) -> str:
        """Generate ICS calendar file content.

        Args:
            summary: Event title
            description: Event description
            start_time: Event start time
            end_time: Event end time
            timezone: Timezone
            location: Event location
            uid: Unique event ID

        Returns:
            ICS file content as string
        """
        # Format times for ICS (YYYYMMDDTHHMMSSZ)
        start_ics = start_time.strftime('%Y%m%dT%H%M%S')
        end_ics = end_time.strftime('%Y%m%dT%H%M%S')
        now_ics = datetime.now().strftime('%Y%m%dT%H%M%S')

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//UnoBot//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{now_ics}Z
DTSTART;TZID={timezone}:{start_ics}
DTEND;TZID={timezone}:{end_ics}
SUMMARY:{summary}
DESCRIPTION:{description}
LOCATION:{location}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT24H
ACTION:DISPLAY
DESCRIPTION:Reminder: 24 hours before
END:VALARM
BEGIN:VALARM
TRIGGER:-PT1H
ACTION:DISPLAY
DESCRIPTION:Reminder: 1 hour before
END:VALARM
END:VEVENT
END:VCALENDAR"""

        return ics_content

    async def send_expert_notification(
        self,
        expert_email: str,
        expert_name: str,
        client_name: str,
        client_email: str,
        start_time: datetime,
        end_time: datetime,
        timezone: str,
        prd_content: str | None = None,
        meeting_link: str | None = None,
    ) -> bool:
        """Send notification email to expert about new booking.

        Args:
            expert_email: Expert's email address
            expert_name: Expert's name
            client_name: Client's name
            client_email: Client's email
            start_time: Booking start time
            end_time: Booking end time
            timezone: Timezone
            prd_content: PRD content (optional)
            meeting_link: Meeting link (optional)

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"📅 New Booking: {client_name} - {start_time.strftime('%b %d, %Y')}"

        # Format date and time
        date_str = start_time.strftime('%A, %B %d, %Y')
        start_time_str = start_time.strftime('%I:%M %p')
        end_time_str = end_time.strftime('%I:%M %p')

        # Build email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 25px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h2 style="margin: 0; font-size: 20px;">New Booking Confirmed 🎉</h2>
                </div>

                <div style="padding: 20px; background: #ffffff; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px;">
                    <p style="margin: 0 0 20px 0;">Hi {expert_name},</p>

                    <p style="margin: 0 0 15px 0;">You have a new consultation booking:</p>

                    <div style="background: #f0fdf4; padding: 15px; border-radius: 6px; border: 1px solid #bbf7d0; margin-bottom: 20px;">
                        <div style="font-weight: 600; font-size: 16px; margin-bottom: 8px;">👤 {client_name}</div>
                        <div style="color: #059669; margin-bottom: 10px;">📧 {client_email}</div>
                        <div style="font-weight: 600; color: #166534; margin-bottom: 5px;">📅 {date_str}</div>
                        <div style="color: #166534;">⏰ {start_time_str} - {end_time_str} ({timezone})</div>
                    </div>
        """

        if meeting_link:
            body += f"""
                    <div style="margin: 15px 0;">
                        <p style="margin: 0 0 8px 0; font-weight: 600;">Meeting Link:</p>
                        <a href="{meeting_link}" style="color: #2563EB; text-decoration: underline;">{meeting_link}</a>
                    </div>
            """

        if prd_content:
            # Truncate PRD for email preview
            prd_preview = prd_content[:500] + "..." if len(prd_content) > 500 else prd_content
            prd_preview_html = prd_preview.replace('\n', '<br>')
            body += f"""
                    <div style="margin: 15px 0;">
                        <p style="margin: 0 0 8px 0; font-weight: 600;">Project Details:</p>
                        <div style="background: #f9fafb; padding: 12px; border-radius: 4px; font-size: 13px; color: #374151; max-height: 200px; overflow-y: auto;">
                            {prd_preview_html}
                        </div>
                    </div>
            """

        body += """
                    <div style="margin: 20px 0; padding: 15px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px;">
                        <p style="margin: 0 0 10px 0; font-weight: 600; color: #1e40af;">Action Required:</p>
                        <ul style="margin: 0; padding-left: 20px; color: #1e40af; font-size: 14px;">
                            <li style="margin-bottom: 5px;">Review the client's project requirements</li>
                            <li style="margin-bottom: 5px;">Prepare for the consultation</li>
                            <li>Add this appointment to your calendar</li>
                        </ul>
                    </div>

                    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                        <p style="margin: 0; font-size: 12px; color: #6b7280;">
                            This booking was made through UnoBot. If you need to make changes,
                            please contact the admin dashboard.
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # In development/test mode, log the email
        if self.environment in ["test", "development"]:
            print(f"\n{'='*60}")
            print("EXPERT NOTIFICATION - Development Mode")
            print(f"{'='*60}")
            print(f"To: {expert_email}")
            print(f"Subject: {subject}")
            print(f"{'='*60}\n")
            return True

        # Production: Send via SendGrid
        try:
            import base64

            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Attachment, Mail

            message = Mail(
                from_email=self.from_email,
                to_emails=expert_email,
                subject=subject,
                html_content=body
            )

            # Attach PRD as .md file if available
            if prd_content:
                prd_bytes = prd_content.encode('utf-8')
                attachment = Attachment(
                    file_content=base64.b64encode(prd_bytes).decode(),
                    file_name="project_requirements.md",
                    file_type="text/markdown",
                    disposition="attachment"
                )
                message.attachment = attachment

            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            return int(response.status_code) == 202

        except ImportError:
            print("SendGrid not installed. Install with: pip install sendgrid")
            return False
        except Exception as e:
            print(f"Error sending expert notification: {e}")
            return False

    async def send_cancellation_email(
        self,
        client_email: str,
        client_name: str,
        expert_name: str,
        start_time: datetime,
        end_time: datetime,
        timezone: str,
    ) -> bool:
        """Send cancellation confirmation email.

        Args:
            client_email: Client's email address
            client_name: Client's name
            expert_name: Expert's name
            start_time: Original booking start time
            end_time: Original booking end time
            timezone: Timezone for the booking

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"❌ Booking Cancelled - Consultation with {expert_name}"

        # Format date and time
        date_str = start_time.strftime('%A, %B %d, %Y')
        start_time_str = start_time.strftime('%I:%M %p')

        # Build email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1 style="margin: 0; font-size: 24px;">Booking Cancelled</h1>
                </div>

                <!-- Content -->
                <div style="padding: 30px; background: #f9fafb; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px;">
                    <p style="margin: 0 0 20px 0;">Hi {client_name},</p>

                    <p style="margin: 0 0 20px 0;">Your consultation appointment with <strong>{expert_name}</strong> has been cancelled.</p>

                    <!-- Original Appointment Details -->
                    <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb; margin-bottom: 20px;">
                        <div style="font-weight: bold; font-size: 16px; color: #111827; margin-bottom: 5px;">Original Appointment</div>
                        <div style="background: #fee2e2; padding: 10px; border-radius: 4px; margin-top: 10px;">
                            <div style="font-weight: 600; color: #991b1b; margin-bottom: 5px;">📅 {date_str}</div>
                            <div style="color: #991b1b;">⏰ {start_time_str} ({timezone})</div>
                        </div>
                    </div>

                    <!-- Next Steps -->
                    <div style="margin: 20px 0; padding: 15px; background: #fef3c7; border: 1px solid #fcd34d; border-radius: 6px;">
                        <p style="margin: 0 0 10px 0; font-weight: 600; color: #92400e;">What's Next?</p>
                        <ul style="margin: 0; padding-left: 20px; color: #92400e; font-size: 14px;">
                            <li style="margin-bottom: 5px;">If you need to reschedule, please visit our website or contact us</li>
                            <li>Your calendar event has been removed (if applicable)</li>
                        </ul>
                    </div>

                    <!-- Footer -->
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 12px;">
                        <p style="margin: 0;">UnoBot - AI Business Consultant</p>
                        <p style="margin: 5px 0 0 0;">Powered by UnoDigit</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # In development/test mode, log the email
        if self.environment in ["test", "development"]:
            print(f"\\n{'='*60}")
            print("CANCELLATION EMAIL - Development Mode")
            print(f"{'='*60}")
            print(f"To: {client_email}")
            print(f"Subject: {subject}")
            print(f"{'='*60}\\n")
            return True

        # Production: Send via SendGrid
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=self.from_email,
                to_emails=client_email,
                subject=subject,
                html_content=body
            )

            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            return int(response.status_code) == 202

        except ImportError:
            print("SendGrid not installed. Install with: pip install sendgrid")
            return False
        except Exception as e:
            print(f"Error sending cancellation email: {e}")
            return False

    async def send_expert_cancellation_notification(
        self,
        expert_email: str,
        expert_name: str,
        client_name: str,
        client_email: str,
        start_time: datetime,
        end_time: datetime,
        timezone: str,
    ) -> bool:
        """Send cancellation notification to expert.

        Args:
            expert_email: Expert's email address
            expert_name: Expert's name
            client_name: Client's name
            client_email: Client's email
            start_time: Original booking start time
            end_time: Original booking end time
            timezone: Timezone for the booking

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"📅 Booking Cancelled: {client_name} - {start_time.strftime('%b %d, %Y')}"

        # Format date and time
        date_str = start_time.strftime('%A, %B %d, %Y')
        start_time_str = start_time.strftime('%I:%M %p')
        end_time_str = end_time.strftime('%I:%M %p')

        # Build email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #dc2626, #b91c1c); color: white; padding: 25px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h2 style="margin: 0; font-size: 20px;">Booking Cancelled</h2>
                </div>

                <div style="padding: 20px; background: #ffffff; border: 1px solid #e5e7eb; border-top: none; border-radius: 0 0 8px 8px;">
                    <p style="margin: 0 0 20px 0;">Hi {expert_name},</p>

                    <p style="margin: 0 0 15px 0;">A consultation booking has been cancelled:</p>

                    <div style="background: #fee2e2; padding: 15px; border-radius: 6px; border: 1px solid #fecaca; margin-bottom: 20px;">
                        <div style="font-weight: 600; font-size: 16px; color: #991b1b; margin-bottom: 8px;">👤 {client_name}</div>
                        <div style="color: #991b1b; margin-bottom: 10px;">📧 {client_email}</div>
                        <div style="font-weight: 600; color: #991b1b; margin-bottom: 5px;">📅 {date_str}</div>
                        <div style="color: #991b1b;">⏰ {start_time_str} - {end_time_str} ({timezone})</div>
                    </div>

                    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e5e7eb;">
                        <p style="margin: 0; font-size: 12px; color: #6b7280;">
                            The calendar event has been removed. This slot is now available for other bookings.
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # In development/test mode, log the email
        if self.environment in ["test", "development"]:
            print(f"\\n{'='*60}")
            print("EXPERT CANCELLATION NOTIFICATION - Development Mode")
            print(f"{'='*60}")
            print(f"To: {expert_email}")
            print(f"Subject: {subject}")
            print(f"{'='*60}\\n")
            return True

        # Production: Send via SendGrid
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=self.from_email,
                to_emails=expert_email,
                subject=subject,
                html_content=body
            )

            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            return int(response.status_code) == 202

        except ImportError:
            print("SendGrid not installed. Install with: pip install sendgrid")
            return False
        except Exception as e:
            print(f"Error sending expert cancellation notification: {e}")
            return False
