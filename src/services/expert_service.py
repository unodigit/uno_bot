"""Expert service for business logic."""
import uuid
from collections import defaultdict

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

    async def match_experts(
        self,
        service_type: str | None = None,
        specialties: list[str] | None = None,
        business_context: dict | None = None,
    ) -> list[tuple[Expert, float]]:
        """Match experts based on service type, specialties, and business context.

        Args:
            service_type: The recommended service type (e.g., "AI Strategy & Planning")
            specialties: List of required specialties
            business_context: Additional business context for matching

        Returns:
            List of (expert, score) tuples sorted by score descending
        """
        # Get all active experts
        experts = await self.list_active_experts()

        if not experts:
            return []

        # Calculate match scores for each expert
        scored_experts = []
        for expert in experts:
            score = self._calculate_match_score(
                expert, service_type, specialties, business_context
            )
            if score > 0:  # Only include experts with positive scores
                scored_experts.append((expert, score))

        # Sort by score descending
        scored_experts.sort(key=lambda x: x[1], reverse=True)

        return scored_experts

    def _calculate_match_score(
        self,
        expert: Expert,
        service_type: str | None,
        specialties: list[str] | None,
        business_context: dict | None,
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

    def _extract_keywords(self, business_context: dict) -> list[str]:
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
