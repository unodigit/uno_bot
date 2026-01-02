"""Expert service for business logic."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.expert import Expert
from src.schemas.expert import ExpertCreate, ExpertUpdate


class ExpertService:
    """Service for managing expert profiles."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_active_experts(self) -> list[Expert]:
        """List all active experts.

        Returns:
            List of active expert profiles
        """
        result = await self.db.execute(
            select(Expert).where(Expert.is_active == True)  # noqa: E712
        )
        return list(result.scalars().all())

    async def get_expert(self, expert_id: uuid.UUID) -> Expert | None:
        """Get an expert by ID.

        Args:
            expert_id: The expert ID

        Returns:
            The expert or None if not found
        """
        result = await self.db.execute(
            select(Expert).where(Expert.id == expert_id)
        )
        return result.scalar_one_or_none()

    async def create_expert(self, expert_create: ExpertCreate) -> Expert:
        """Create a new expert.

        Args:
            expert_create: The expert creation data

        Returns:
            The created expert
        """
        expert = Expert(
            name=expert_create.name,
            email=expert_create.email,
            photo_url=expert_create.photo_url,
            role=expert_create.role,
            bio=expert_create.bio,
            specialties=expert_create.specialties or [],
            services=expert_create.services or [],
            availability=expert_create.availability or {},
            is_active=expert_create.is_active if expert_create.is_active is not None else True,
        )

        self.db.add(expert)
        await self.db.commit()
        await self.db.refresh(expert)

        return expert

    async def update_expert(self, expert: Expert, expert_update: ExpertUpdate) -> Expert:
        """Update an expert.

        Args:
            expert: The existing expert
            expert_update: The update data

        Returns:
            The updated expert
        """
        # Update fields if provided
        if expert_update.name is not None:
            expert.name = expert_update.name
        if expert_update.email is not None:
            expert.email = expert_update.email
        if expert_update.photo_url is not None:
            expert.photo_url = expert_update.photo_url
        if expert_update.role is not None:
            expert.role = expert_update.role
        if expert_update.bio is not None:
            expert.bio = expert_update.bio
        if expert_update.specialties is not None:
            expert.specialties = expert_update.specialties
        if expert_update.services is not None:
            expert.services = expert_update.services
        if expert_update.availability is not None:
            expert.availability = expert_update.availability
        if expert_update.is_active is not None:
            expert.is_active = expert_update.is_active
        if expert_update.calendar_id is not None:
            expert.calendar_id = expert_update.calendar_id
        if expert_update.refresh_token is not None:
            expert.refresh_token = expert_update.refresh_token

        self.db.add(expert)
        await self.db.commit()
        await self.db.refresh(expert)

        return expert

    async def delete_expert(self, expert: Expert) -> None:
        """Delete an expert.

        Args:
            expert: The expert to delete
        """
        await self.db.delete(expert)
        await self.db.commit()
