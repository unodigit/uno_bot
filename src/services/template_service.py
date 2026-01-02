"""Service for managing welcome message templates."""
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.template import WelcomeMessageTemplate
from src.schemas.template import WelcomeMessageTemplateCreate, WelcomeMessageTemplateUpdate


class TemplateService:
    """Service for managing welcome message templates."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_template(
        self, template_create: WelcomeMessageTemplateCreate
    ) -> WelcomeMessageTemplate:
        """Create a new welcome message template."""
        # If this is set as default, unset other defaults
        if template_create.is_default:
            await self._unset_all_defaults()

        template = WelcomeMessageTemplate(**template_create.model_dump())
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def get_template(self, template_id: uuid.UUID) -> Optional[WelcomeMessageTemplate]:
        """Get a template by ID."""
        result = await self.db.execute(
            select(WelcomeMessageTemplate).where(WelcomeMessageTemplate.id == template_id)
        )
        return result.scalar_one_or_none()

    async def get_all_templates(self) -> List[WelcomeMessageTemplate]:
        """Get all templates."""
        result = await self.db.execute(
            select(WelcomeMessageTemplate).order_by(WelcomeMessageTemplate.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_active_templates(self) -> List[WelcomeMessageTemplate]:
        """Get all active templates."""
        result = await self.db.execute(
            select(WelcomeMessageTemplate)
            .where(WelcomeMessageTemplate.is_active == True)
            .order_by(WelcomeMessageTemplate.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_default_template(self) -> Optional[WelcomeMessageTemplate]:
        """Get the default template."""
        result = await self.db.execute(
            select(WelcomeMessageTemplate)
            .where(WelcomeMessageTemplate.is_default == True)
            .where(WelcomeMessageTemplate.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_template_for_industry(
        self, industry: Optional[str] = None
    ) -> Optional[WelcomeMessageTemplate]:
        """Get a template suitable for the given industry."""
        if not industry:
            return await self.get_default_template()

        # First try to find an industry-specific active template
        result = await self.db.execute(
            select(WelcomeMessageTemplate)
            .where(WelcomeMessageTemplate.is_active == True)
            .where(
                WelcomeMessageTemplate.target_industry.ilike(f"%{industry.lower()}%")
            )
            .order_by(WelcomeMessageTemplate.use_count.desc())
            .limit(1)
        )
        template = result.scalar_one_or_none()

        # Fall back to default template
        if not template:
            template = await self.get_default_template()

        return template

    async def update_template(
        self, template_id: uuid.UUID, template_update: WelcomeMessageTemplateUpdate
    ) -> Optional[WelcomeMessageTemplate]:
        """Update a template."""
        template = await self.get_template(template_id)
        if not template:
            return None

        update_data = template_update.model_dump(exclude_unset=True)

        # Handle default flag
        if "is_default" in update_data and update_data["is_default"]:
            await self._unset_all_defaults()

        for field, value in update_data.items():
            setattr(template, field, value)

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        return template

    async def delete_template(self, template_id: uuid.UUID) -> bool:
        """Delete a template."""
        template = await self.get_template(template_id)
        if not template:
            return False

        await self.db.delete(template)
        await self.db.commit()
        return True

    async def increment_use_count(self, template_id: uuid.UUID) -> None:
        """Increment the use count of a template."""
        template = await self.get_template(template_id)
        if template:
            template.use_count += 1
            self.db.add(template)
            await self.db.commit()

    async def _unset_all_defaults(self) -> None:
        """Unset the default flag on all templates."""
        result = await self.db.execute(
            select(WelcomeMessageTemplate).where(WelcomeMessageTemplate.is_default == True)
        )
        templates = result.scalars().all()
        for template in templates:
            template.is_default = False
            self.db.add(template)
        await self.db.commit()
