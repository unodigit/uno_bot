"""Expert service for business logic."""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import decrypt_oauth_token, encrypt_oauth_token
from src.models.booking import Booking
from src.models.expert import Expert
from src.schemas.expert import ExpertCreate, ExpertResponse, ExpertUpdate
from src.services.cache_service import cache_expert_data, get_cached_expert_data


class ExpertService:
    """Service for managing expert profiles."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_active_experts(self) -> list[ExpertResponse]:
        """List all active experts.

        Returns:
            List of active expert profiles
        """
        result = await self.db.execute(
            select(Expert).where(Expert.is_active == True)  # noqa: E712
        )
        experts = result.scalars().all()
        return [ExpertResponse.model_validate(e) for e in experts]

    async def list_experts(self, include_inactive: bool = False) -> list[ExpertResponse]:
        """List all experts (optionally including inactive ones).

        Args:
            include_inactive: Whether to include inactive experts

        Returns:
            List of expert profiles
        """
        if include_inactive:
            result = await self.db.execute(
                select(Expert)
            )
        else:
            result = await self.db.execute(
                select(Expert).where(Expert.is_active == True)  # noqa: E712
            )
        experts = result.scalars().all()
        return [ExpertResponse.model_validate(e) for e in experts]

    async def count_experts(self, active_only: bool = False) -> int:
        """Count total number of experts.

        Args:
            active_only: Whether to count only active experts

        Returns:
            Number of experts
        """
        if active_only:
            result = await self.db.execute(
                select(func.count()).select_from(Expert).where(Expert.is_active == True)  # noqa: E712
            )
        else:
            result = await self.db.execute(
                select(func.count()).select_from(Expert)
            )
        return result.scalar_one()

    async def get_expert(self, expert_id: uuid.UUID) -> ExpertResponse | None:
        """Get an expert by ID with caching.
        Args:
            expert_id: The expert ID
        Returns:
            The expert or None if not found
        """
        # Try to get from cache first
        cached_expert = await get_cached_expert_data(str(expert_id))
        if cached_expert:
            # Reconstruct the ExpertResponse from cached data
            return ExpertResponse(**cached_expert)

        # If not cached, get from database
        result = await self.db.execute(
            select(Expert).where(Expert.id == expert_id)
        )
        expert = result.scalar_one_or_none()
        if expert:
            expert_response = ExpertResponse.model_validate(expert)
            expert_data = expert_response.model_dump()
            # Cache the expert data
            await cache_expert_data(str(expert_id), expert_data)
            return expert_response
        return None

    async def get_expert_model(self, expert_id: uuid.UUID) -> Expert | None:
        """Get an expert model by ID (internal helper for updates).

        Args:
            expert_id: The expert ID

        Returns:
            The expert model or None if not found
        """
        result = await self.db.execute(
            select(Expert).where(Expert.id == expert_id)
        )
        return result.scalar_one_or_none()

    async def match_experts(
        self,
        service_type: str | None = None,
        specialties: list[str] | None = None,
        business_context: dict[str, Any] | None = None,
        workload_balancing: bool = True,
    ) -> list[tuple[ExpertResponse, float]]:
        """Match experts based on service type, specialties, and business context.

        Args:
            service_type: The recommended service type (e.g., "AI Strategy & Planning")
            specialties: List of required specialties
            business_context: Additional business context for matching
            workload_balancing: Whether to factor in expert workload (active bookings)

        Returns:
            List of (expert, score) tuples sorted by score descending
        """
        # Get all active experts
        experts_models = await self.list_active_experts()

        if not experts_models:
            return []

        # Get workload counts for all experts
        workload_map = {}
        if workload_balancing:
            workload_map = await self._get_expert_workload_counts()

        # Calculate match scores for each expert
        scored_experts = []
        for expert_response in experts_models:
            # Get the model for scoring (need to access raw data)
            expert_model = await self.get_expert_model(expert_response.id)
            if not expert_model:
                continue

            score = self._calculate_match_score(
                expert_model, service_type, specialties, business_context
            )
            if score > 0:  # Only include experts with positive scores
                # Apply workload penalty if enabled
                if workload_balancing:
                    workload_penalty = self._calculate_workload_penalty(
                        expert_response.id, workload_map
                    )
                    score = score * workload_penalty
                scored_experts.append((expert_response, score))

        # Sort by score descending
        scored_experts.sort(key=lambda x: x[1], reverse=True)

        return scored_experts

    async def _get_expert_workload_counts(self) -> dict[uuid.UUID, int]:
        """Get count of active bookings for each expert.

        Returns:
            Dictionary mapping expert_id to number of active bookings
        """
        # Count bookings that are confirmed and in the future (active workload)
        future_bookings = select(
            Booking.expert_id,
            func.count(Booking.id).label('booking_count')
        ).where(
            Booking.status == 'confirmed'
        ).where(
            Booking.start_time >= datetime.utcnow()
        ).group_by(
            Booking.expert_id
        )

        result = await self.db.execute(future_bookings)
        workload_map = {row[0]: row[1] for row in result.all()}

        return workload_map

    def _calculate_workload_penalty(self, expert_id: uuid.UUID, workload_map: dict[uuid.UUID, int]) -> float:
        """Calculate workload penalty based on active bookings.

        Args:
            expert_id: The expert's ID
            workload_map: Dictionary of expert_id to booking count

        Returns:
            Penalty multiplier between 0.5 and 1.0
        """
        workload = workload_map.get(expert_id, 0)

        # Penalty tiers:
        # 0 bookings: 1.0 (no penalty)
        # 1-2 bookings: 0.95 (minimal penalty)
        # 3-4 bookings: 0.9 (light penalty)
        # 5-6 bookings: 0.8 (moderate penalty)
        # 7+ bookings: 0.7 (heavy penalty)
        if workload == 0:
            return 1.0
        elif workload <= 2:
            return 0.95
        elif workload <= 4:
            return 0.9
        elif workload <= 6:
            return 0.8
        else:
            return 0.7

    def _calculate_match_score(
        self,
        expert: Expert,
        service_type: str | None,
        specialties: list[str] | None,
        business_context: dict[str, Any] | None,
    ) -> float:
        """Calculate a match score for an expert.

        Args:
            expert: The expert to score
            service_type: The recommended service type
            specialties: Required specialties
            business_context: Business context for keyword matching

        Returns:
            Match score between 0 and 100
        """
        score = 0.0

        # Service type matching (40 points max)
        if service_type and expert.services:
            if service_type in expert.services:
                score += 40.0  # Exact match
            else:
                # Partial match based on keywords
                service_lower = service_type.lower()
                for expert_service in expert.services:
                    if any(
                        keyword in expert_service.lower()
                        for keyword in service_lower.split()
                    ):
                        score += 20.0
                        break

        # Specialty matching (30 points max)
        if specialties and expert.specialties:
            matched_specialties = set(specialties) & set(expert.specialties)
            if matched_specialties:
                # Proportional score based on how many specialties match
                specialty_score = (len(matched_specialties) / len(specialties)) * 30.0
                score += specialty_score

        # Business context keyword matching (30 points max)
        if business_context and expert.specialties:
            context_keywords = self._extract_keywords(business_context)
            specialty_keywords = [s.lower() for s in expert.specialties]

            matched_keywords = set(context_keywords) & set(specialty_keywords)
            if matched_keywords and context_keywords:
                # Proportional score based on keyword overlap
                keyword_score = (len(matched_keywords) / len(context_keywords)) * 30.0
                score += min(keyword_score, 30.0)  # Cap at 30

        return min(score, 100.0)  # Ensure max score is 100

    def _extract_keywords(self, business_context: dict[str, Any]) -> list[str]:
        """Extract keywords from business context.

        Args:
            business_context: Dictionary containing challenges, industry, tech_stack

        Returns:
            List of lowercase keywords
        """
        keywords = []

        # Extract from challenges
        challenges = business_context.get("challenges", "")
        if challenges:
            keywords.extend(challenges.lower().split())

        # Extract from industry
        industry = business_context.get("industry", "")
        if industry:
            keywords.append(industry.lower())

        # Extract from tech stack
        tech_stack = business_context.get("tech_stack", "")
        if tech_stack:
            keywords.extend(tech_stack.lower().split())

        return [k for k in keywords if len(k) > 2]  # Filter short words

    async def create_expert(self, expert_create: ExpertCreate) -> ExpertResponse:
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

        return ExpertResponse.model_validate(expert)

    async def update_expert(self, expert: Expert, expert_update: ExpertUpdate) -> ExpertResponse:
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
            expert.refresh_token = encrypt_oauth_token(expert_update.refresh_token)

        self.db.add(expert)
        await self.db.commit()
        await self.db.refresh(expert)

        return ExpertResponse.model_validate(expert)

    async def deactivate_expert(self, expert: Expert) -> ExpertResponse:
        """Deactivate an expert.

        Args:
            expert: The expert to deactivate

        Returns:
            The deactivated expert
        """
        expert.is_active = False
        self.db.add(expert)
        await self.db.commit()
        await self.db.refresh(expert)
        return ExpertResponse.model_validate(expert)

    async def delete_expert(self, expert: Expert) -> None:
        """Delete an expert.

        Args:
            expert: The expert to delete
        """
        await self.db.delete(expert)
        await self.db.commit()
