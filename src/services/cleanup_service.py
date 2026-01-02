"""Session cleanup service for managing session lifecycle and cleanup."""
import uuid
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.prd import PRDDocument
from src.models.session import ConversationSession, Message, SessionStatus


class CleanupService:
    """Service for cleaning up old sessions and related data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def cleanup_old_sessions(self, max_age_days: int = 7) -> int:
        """Clean up sessions older than max_age_days.

        Args:
            max_age_days: Maximum age in days for sessions to keep

        Returns:
            Number of sessions deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

        # Find sessions to delete
        result = await self.db.execute(
            select(ConversationSession.id)
            .where(
                and_(
                    ConversationSession.status.in_([
                        SessionStatus.COMPLETED.value,
                        SessionStatus.ABANDONED.value
                    ]),
                    ConversationSession.completed_at < cutoff_date
                )
            )
        )
        session_ids = [row[0] for row in result.fetchall()]

        if not session_ids:
            return 0

        # Delete related messages first
        await self.db.execute(
            delete(Message).where(Message.session_id.in_(session_ids))
        )

        # Delete related PRDs
        await self.db.execute(
            delete(PRDDocument).where(PRDDocument.session_id.in_(session_ids))
        )

        # Delete sessions
        delete_result = await self.db.execute(
            delete(ConversationSession).where(ConversationSession.id.in_(session_ids))
        )

        await self.db.commit()
        return delete_result.rowcount  # type: ignore[attr-defined, no-any-return]

    async def cleanup_expired_prds(self, max_age_days: int = 90) -> int:
        """Clean up PRDs older than max_age_days.

        Args:
            max_age_days: Maximum age in days for PRDs to keep

        Returns:
            Number of PRDs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

        # Find PRDs to delete
        result = await self.db.execute(
            select(PRDDocument.id)
            .where(PRDDocument.created_at < cutoff_date)
        )
        prd_ids = [row[0] for row in result.fetchall()]

        if not prd_ids:
            return 0

        # Delete PRDs
        delete_result = await self.db.execute(
            delete(PRDDocument).where(PRDDocument.id.in_(prd_ids))
        )

        await self.db.commit()
        return delete_result.rowcount  # type: ignore[attr-defined, no-any-return]

    async def get_session_stats(self) -> dict:
        """Get session statistics for monitoring.

        Returns:
            Dictionary with session statistics
        """
        # Count sessions by status
        result = await self.db.execute(
            select(ConversationSession.status, ConversationSession.completed_at)
            .order_by(ConversationSession.started_at)
        )
        sessions = result.fetchall()

        stats = {
            "total_sessions": len(sessions),
            "active_sessions": 0,
            "completed_sessions": 0,
            "abandoned_sessions": 0,
            "sessions_older_than_7_days": 0,
            "sessions_older_than_30_days": 0,
        }

        cutoff_7_days = datetime.utcnow() - timedelta(days=7)
        cutoff_30_days = datetime.utcnow() - timedelta(days=30)

        for status, completed_at in sessions:
            if status == SessionStatus.ACTIVE.value:
                stats["active_sessions"] += 1
            elif status == SessionStatus.COMPLETED.value:
                stats["completed_sessions"] += 1
            elif status == SessionStatus.ABANDONED.value:
                stats["abandoned_sessions"] += 1

            if completed_at:
                if completed_at < cutoff_7_days:
                    stats["sessions_older_than_7_days"] += 1
                if completed_at < cutoff_30_days:
                    stats["sessions_older_than_30_days"] += 1

        return stats

    async def cleanup_orphaned_data(self) -> dict:
        """Clean up orphaned data (messages and PRDs without sessions).

        Returns:
            Dictionary with cleanup results
        """
        # Find orphaned messages
        result = await self.db.execute(
            select(Message.id)
            .outerjoin(ConversationSession, Message.session_id == ConversationSession.id)
            .where(ConversationSession.id.is_(None))
        )
        orphaned_message_ids = [row[0] for row in result.fetchall()]

        # Delete orphaned messages
        messages_deleted = 0
        if orphaned_message_ids:
            delete_result = await self.db.execute(
                delete(Message).where(Message.id.in_(orphaned_message_ids))
            )
            messages_deleted = delete_result.rowcount  # type: ignore[attr-defined]

        # Find orphaned PRDs
        result = await self.db.execute(
            select(PRDDocument.id)
            .outerjoin(ConversationSession, PRDDocument.session_id == ConversationSession.id)
            .where(ConversationSession.id.is_(None))
        )
        orphaned_prd_ids = [row[0] for row in result.fetchall()]

        # Delete orphaned PRDs
        prds_deleted = 0
        if orphaned_prd_ids:
            delete_result = await self.db.execute(
                delete(PRDDocument).where(PRDDocument.id.in_(orphaned_prd_ids))
            )
            prds_deleted = delete_result.rowcount  # type: ignore[attr-defined]

        await self.db.commit()

        return {
            "messages_deleted": messages_deleted,
            "prds_deleted": prds_deleted,
        }


def get_cleanup_service(db: AsyncSession) -> CleanupService:
    """Get cleanup service instance."""
    return CleanupService(db)