"""Analytics service for conversation and system metrics."""
import uuid
from datetime import datetime, timedelta
from typing import Any, cast

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.booking import Booking, BookingStatus
from src.models.expert import Expert
from src.models.session import ConversationSession, SessionPhase, SessionStatus


class AnalyticsService:
    """Service for generating conversation and system analytics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_conversation_analytics(self, days_back: int = 30) -> dict[str, Any]:
        """Get comprehensive conversation analytics.

        Args:
            days_back: Number of days to look back for analytics

        Returns:
            Dictionary containing conversation metrics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        # Basic session metrics
        total_sessions = await self._get_total_sessions(start_date, end_date)
        active_sessions = await self._get_active_sessions(start_date, end_date)
        completed_sessions = await self._get_completed_sessions(start_date, end_date)
        abandoned_sessions = await self._get_abandoned_sessions(start_date, end_date)

        # Conversion metrics
        sessions_with_prd = await self._get_sessions_with_prd(start_date, end_date)
        sessions_with_booking = await self._get_sessions_with_booking(start_date, end_date)

        # Engagement metrics
        avg_session_duration = await self._get_average_session_duration(start_date, end_date)
        avg_messages_per_session = await self._get_average_messages_per_session(start_date, end_date)
        lead_score_stats = await self._get_lead_score_statistics(start_date, end_date)

        # Service recommendation analytics
        service_distribution = await self._get_service_recommendation_distribution(start_date, end_date)

        # Phase completion rates
        phase_completion_rates = await self._get_phase_completion_rates(start_date, end_date)

        # Daily metrics for trend analysis
        daily_metrics = await self._get_daily_metrics(start_date, end_date)

        return {
            "time_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_back": days_back
            },
            "sessions": {
                "total": total_sessions,
                "active": active_sessions,
                "completed": completed_sessions,
                "abandoned": abandoned_sessions,
                "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
            },
            "conversion_metrics": {
                "sessions_with_prd": sessions_with_prd,
                "prd_conversion_rate": (sessions_with_prd / total_sessions * 100) if total_sessions > 0 else 0,
                "sessions_with_booking": sessions_with_booking,
                "booking_conversion_rate": (sessions_with_booking / total_sessions * 100) if total_sessions > 0 else 0,
                "prd_to_booking_rate": (sessions_with_booking / sessions_with_prd * 100) if sessions_with_prd > 0 else 0
            },
            "engagement_metrics": {
                "average_session_duration_minutes": avg_session_duration,
                "average_messages_per_session": avg_messages_per_session,
                "lead_score": lead_score_stats
            },
            "service_analytics": {
                "distribution": service_distribution,
                "most_popular_service": max(service_distribution.items(), key=lambda x: x[1])[0] if service_distribution else None
            },
            "phase_analytics": {
                "completion_rates": phase_completion_rates
            },
            "trends": {
                "daily_metrics": daily_metrics
            }
        }

    async def get_expert_analytics(self, days_back: int = 30) -> dict[str, Any]:
        """Get expert performance analytics.

        Args:
            days_back: Number of days to look back for analytics

        Returns:
            Dictionary containing expert performance metrics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        # Get all experts with their booking counts
        expert_bookings = await self._get_expert_booking_counts(start_date, end_date)
        expert_sessions = await self._get_expert_session_counts(start_date, end_date)

        # Get all experts to look up their details
        result = await self.db.execute(select(Expert))
        all_experts = {e.id: e for e in result.scalars().all()}

        # Calculate expert performance metrics
        expert_metrics = []
        for expert_id, booking_count in expert_bookings.items():
            expert = all_experts.get(expert_id)
            if not expert:
                continue
            session_count = expert_sessions.get(expert_id, 0)
            conversion_rate = (booking_count / session_count * 100) if session_count > 0 else 0

            expert_metrics.append({
                "id": expert.id,
                "name": expert.name,
                "email": expert.email,
                "role": expert.role,
                "specialties": expert.specialties,
                "total_sessions": session_count,
                "total_bookings": booking_count,
                "conversion_rate": conversion_rate,
                "availability_status": "active" if expert.is_active else "inactive"
            })

        # Sort by booking count
        expert_metrics.sort(key=lambda x: cast(int, x["total_bookings"]), reverse=True)

        total_bookings: int = sum(cast(int, e["total_bookings"]) for e in expert_metrics)
        avg_bookings: float = total_bookings / len(expert_metrics) if expert_metrics else 0.0

        return {
            "time_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_back": days_back
            },
            "experts": expert_metrics,
            "summary": {
                "total_experts": len(expert_metrics),
                "active_experts": len([e for e in expert_metrics if e["availability_status"] == "active"]),
                "average_bookings_per_expert": avg_bookings
            }
        }

    async def get_booking_analytics(self, days_back: int = 30) -> dict[str, Any]:
        """Get booking performance analytics.

        Args:
            days_back: Number of days to look back for analytics

        Returns:
            Dictionary containing booking metrics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)

        # Basic booking metrics
        total_bookings = await self._get_total_bookings(start_date, end_date)
        confirmed_bookings = await self._get_bookings_by_status(BookingStatus.CONFIRMED, start_date, end_date)
        cancelled_bookings = await self._get_bookings_by_status(BookingStatus.CANCELLED, start_date, end_date)
        completed_bookings = await self._get_bookings_by_status(BookingStatus.COMPLETED, start_date, end_date)

        # Time-based metrics
        avg_lead_time = await self._get_average_lead_time(start_date, end_date)
        booking_time_distribution = await self._get_booking_time_distribution(start_date, end_date)
        booking_day_distribution = await self._get_booking_day_distribution(start_date, end_date)

        # Cancellation analysis
        cancellation_rate = (cancelled_bookings / total_bookings * 100) if total_bookings > 0 else 0
        last_7_days_bookings = await self._get_bookings_by_date_range(start_date + timedelta(days=23), end_date)
        recent_cancellations = await self._get_bookings_by_status(BookingStatus.CANCELLED, start_date + timedelta(days=23), end_date)

        return {
            "time_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_back": days_back
            },
            "bookings": {
                "total": total_bookings,
                "confirmed": confirmed_bookings,
                "cancelled": cancelled_bookings,
                "completed": completed_bookings,
                "cancellation_rate": cancellation_rate,
                "conversion_rate": (confirmed_bookings / total_bookings * 100) if total_bookings > 0 else 0
            },
            "timing": {
                "average_lead_time_days": avg_lead_time,
                "time_distribution": booking_time_distribution,
                "day_distribution": booking_day_distribution
            },
            "recent_trends": {
                "last_7_days_bookings": last_7_days_bookings,
                "recent_cancellations": recent_cancellations,
                "recent_cancellation_rate": (recent_cancellations / last_7_days_bookings * 100) if last_7_days_bookings > 0 else 0
            }
        }

    async def get_system_health(self) -> dict[str, Any]:
        """Get system health and performance metrics.

        Returns:
            Dictionary containing system health status
        """
        try:
            # Test database connection
            result = await self.db.execute(text("SELECT 1"))
            db_status = "healthy" if result.scalar() == 1 else "unhealthy"
        except Exception:
            db_status = "unhealthy"

        # Get basic counts
        try:
            total_experts = await self._get_count(Expert)
            active_sessions = await self._get_active_sessions_count()
            total_bookings = await self._get_count(Booking)
        except Exception:
            total_experts = 0
            active_sessions = 0
            total_bookings = 0

        return {
            "status": "operational" if db_status == "healthy" else "degraded",
            "database": db_status,
            "last_updated": datetime.utcnow().isoformat(),
            "metrics": {
                "total_experts": total_experts,
                "active_sessions": active_sessions,
                "total_bookings": total_bookings
            }
        }

    # Private helper methods

    async def _get_total_sessions(self, start_date: datetime, end_date: datetime) -> int:
        """Get total number of sessions in date range."""
        result = await self.db.execute(
            select(func.count()).select_from(ConversationSession).where(
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            )
        )
        return result.scalar_one()

    async def _get_active_sessions(self, start_date: datetime, end_date: datetime) -> int:
        """Get number of active sessions."""
        result = await self.db.execute(
            select(func.count()).select_from(ConversationSession).where(
                ConversationSession.status == SessionStatus.ACTIVE.value,
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            )
        )
        return result.scalar_one()

    async def _get_completed_sessions(self, start_date: datetime, end_date: datetime) -> int:
        """Get number of completed sessions."""
        result = await self.db.execute(
            select(func.count()).select_from(ConversationSession).where(
                ConversationSession.status == SessionStatus.COMPLETED.value,
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            )
        )
        return result.scalar_one()

    async def _get_abandoned_sessions(self, start_date: datetime, end_date: datetime) -> int:
        """Get number of abandoned sessions."""
        result = await self.db.execute(
            select(func.count()).select_from(ConversationSession).where(
                ConversationSession.status == SessionStatus.ABANDONED.value,
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            )
        )
        return result.scalar_one()

    async def _get_sessions_with_prd(self, start_date: datetime, end_date: datetime) -> int:
        """Get number of sessions that generated a PRD."""
        result = await self.db.execute(
            select(func.count()).select_from(ConversationSession).where(
                ConversationSession.prd_id.isnot(None),
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            )
        )
        return result.scalar_one()

    async def _get_sessions_with_booking(self, start_date: datetime, end_date: datetime) -> int:
        """Get number of sessions that resulted in a booking."""
        result = await self.db.execute(
            select(func.count()).select_from(ConversationSession).where(
                ConversationSession.booking_id.isnot(None),
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            )
        )
        return result.scalar_one()

    async def _get_average_session_duration(self, start_date: datetime, end_date: datetime) -> float:
        """Get average session duration in minutes."""
        result = await self.db.execute(
            select(func.avg(
                func.extract('epoch', ConversationSession.completed_at - ConversationSession.started_at) / 60
            )).select_from(ConversationSession).where(
                ConversationSession.completed_at.isnot(None),
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            )
        )
        avg_duration = result.scalar_one()
        return float(avg_duration) if avg_duration else 0.0

    async def _get_average_messages_per_session(self, start_date: datetime, end_date: datetime) -> float:
        """Get average number of messages per session."""
        # This would require joining with the messages table
        # For now, return a placeholder
        return 0.0

    async def _get_lead_score_statistics(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """Get lead score statistics."""
        result = await self.db.execute(
            select(
                func.avg(ConversationSession.lead_score),
                func.min(ConversationSession.lead_score),
                func.max(ConversationSession.lead_score)
            ).select_from(ConversationSession).where(
                ConversationSession.lead_score.isnot(None),
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            ))
        row = result.fetchone()
        if row:
            avg_score, min_score, max_score = row
        else:
            avg_score, min_score, max_score = None, None, None

        return {
            "average": float(avg_score) if avg_score else 0.0,
            "minimum": int(min_score) if min_score else 0,
            "maximum": int(max_score) if max_score else 0,
            "distribution": await self._get_lead_score_distribution(start_date, end_date)
        }

    async def _get_lead_score_distribution(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """Get lead score distribution buckets."""
        # Group lead scores into buckets
        result = await self.db.execute(
            select(
                func.floor(ConversationSession.lead_score / 20) * 20,
                func.count()
            ).select_from(ConversationSession).where(
                ConversationSession.lead_score.isnot(None),
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            ).group_by(
                func.floor(ConversationSession.lead_score / 20)
            ).order_by(
                func.floor(ConversationSession.lead_score / 20)
            )
        )

        distribution = {}
        for bucket_start, count in result.fetchall():
            bucket_range = f"{int(bucket_start)}-{int(bucket_start) + 19}"
            distribution[bucket_range] = int(count)

        return distribution

    async def _get_service_recommendation_distribution(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """Get distribution of recommended services."""
        result = await self.db.execute(
            select(
                ConversationSession.recommended_service,
                func.count()
            ).select_from(ConversationSession).where(
                ConversationSession.recommended_service.isnot(None),
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            ).group_by(
                ConversationSession.recommended_service
            )
        )

        distribution = {}
        for service, count in result.fetchall():
            distribution[service] = int(count)

        return distribution

    async def _get_phase_completion_rates(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """Get completion rates for each conversation phase."""
        result = await self.db.execute(
            select(
                ConversationSession.current_phase,
                func.count()
            ).select_from(ConversationSession).where(
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            ).group_by(
                ConversationSession.current_phase
            )
        )

        rows = result.fetchall()
        phase_counts: dict[str, int] = {row[0]: row[1] for row in rows}
        total_sessions = sum(phase_counts.values())

        completion_rates = {}
        for phase in SessionPhase:
            phase_count = phase_counts.get(phase.value, 0)
            completion_rates[phase.value] = {
                "count": phase_count,
                "percentage": (phase_count / total_sessions * 100) if total_sessions > 0 else 0
            }

        return completion_rates

    async def _get_daily_metrics(self, start_date: datetime, end_date: datetime) -> list[dict[str, Any]]:
        """Get daily metrics for trend analysis."""
        # This would require more complex date grouping
        # For now, return empty list
        return []

    async def _get_expert_booking_counts(self, start_date: datetime, end_date: datetime) -> dict[uuid.UUID, int]:
        """Get booking counts per expert."""
        result = await self.db.execute(
            select(
                Expert.id,
                func.count(Booking.id)
            ).select_from(Booking).join(Expert).where(
                Booking.start_time >= start_date,
                Booking.start_time <= end_date
            ).group_by(Expert.id)
        )

        rows = result.fetchall()
        return {row[0]: row[1] for row in rows}

    async def _get_expert_session_counts(self, start_date: datetime, end_date: datetime) -> dict[uuid.UUID, int]:
        """Get session counts per expert."""
        result = await self.db.execute(
            select(
                Expert.id,
                func.count(ConversationSession.id)
            ).select_from(ConversationSession).join(Expert, Expert.id == ConversationSession.matched_expert_id).where(
                ConversationSession.started_at >= start_date,
                ConversationSession.started_at <= end_date
            ).group_by(Expert.id)
        )

        rows = result.fetchall()
        return {row[0]: row[1] for row in rows}

    async def _get_total_bookings(self, start_date: datetime, end_date: datetime) -> int:
        """Get total number of bookings."""
        result = await self.db.execute(
            select(func.count()).select_from(Booking).where(
                Booking.start_time >= start_date,
                Booking.start_time <= end_date
            )
        )
        return result.scalar_one()

    async def _get_bookings_by_status(self, status: BookingStatus, start_date: datetime, end_date: datetime) -> int:
        """Get number of bookings by status."""
        result = await self.db.execute(
            select(func.count()).select_from(Booking).where(
                Booking.status == status.value,
                Booking.start_time >= start_date,
                Booking.start_time <= end_date
            )
        )
        return result.scalar_one()

    async def _get_bookings_by_date_range(self, start_date: datetime, end_date: datetime) -> int:
        """Get number of bookings in date range."""
        result = await self.db.execute(
            select(func.count()).select_from(Booking).where(
                Booking.start_time >= start_date,
                Booking.start_time <= end_date
            )
        )
        return result.scalar_one()

    async def _get_average_lead_time(self, start_date: datetime, end_date: datetime) -> float:
        """Get average lead time in days."""
        result = await self.db.execute(
            select(func.avg(
                func.extract('epoch', Booking.start_time - Booking.created_at) / (60 * 60 * 24)
            )).select_from(Booking).where(
                Booking.start_time >= start_date,
                Booking.start_time <= end_date
            )
        )
        avg_lead_time = result.scalar_one()
        return float(avg_lead_time) if avg_lead_time else 0.0

    async def _get_booking_time_distribution(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """Get booking time distribution by hour."""
        # Extract hour from start_time and count
        result = await self.db.execute(
            select(
                func.extract('hour', Booking.start_time),
                func.count()
            ).select_from(Booking).where(
                Booking.start_time >= start_date,
                Booking.start_time <= end_date
            ).group_by(
                func.extract('hour', Booking.start_time)
            ).order_by(
                func.extract('hour', Booking.start_time)
            )
        )

        distribution = {}
        for hour, count in result.fetchall():
            distribution[f"{int(hour)}:00"] = int(count)

        return distribution

    async def _get_booking_day_distribution(self, start_date: datetime, end_date: datetime) -> dict[str, Any]:
        """Get booking day distribution."""
        # Extract day of week from start_time and count
        result = await self.db.execute(
            select(
                func.extract('dow', Booking.start_time),  # Day of week (0=Sunday)
                func.count()
            ).select_from(Booking).where(
                Booking.start_time >= start_date,
                Booking.start_time <= end_date
            ).group_by(
                func.extract('dow', Booking.start_time)
            ).order_by(
                func.extract('dow', Booking.start_time)
            )
        )

        day_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        distribution = {}
        for dow, count in result.fetchall():
            distribution[day_names[int(dow)]] = int(count)

        return distribution

    async def _get_count(self, model) -> int:
        """Get total count of a model."""
        result = await self.db.execute(select(func.count()).select_from(model))
        return result.scalar_one()

    async def _get_active_sessions_count(self) -> int:
        """Get current number of active sessions."""
        result = await self.db.execute(
            select(func.count()).select_from(ConversationSession).where(
                ConversationSession.status == SessionStatus.ACTIVE.value
            )
        )
        return result.scalar_one()
