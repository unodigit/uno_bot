"""Upload API routes for file uploads."""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.security import require_admin_auth
from src.services.expert_service import ExpertService

router = APIRouter()

# Upload directory
UPLOAD_DIR: Path = settings.upload_dir
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return os.path.splitext(filename)[1].lower()


def is_allowed_file_type(content_type: str, filename: str) -> bool:
    """Check if file type is allowed."""
    allowed_types = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
    }

    # Also check by extension as backup
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    extension = get_file_extension(filename)

    return content_type in allowed_types or extension in allowed_extensions


@router.post(
    "/expert-photo/{expert_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Upload expert profile photo",
    description="Upload a profile photo for an expert. Returns the URL to access the photo."
)
async def upload_expert_photo(
    expert_id: str,
    file: Annotated[UploadFile, File(description="Profile photo image file")],
    db: AsyncSession = Depends(get_db),
    admin_data: dict = Depends(require_admin_auth),
):
    """Upload a profile photo for an expert.

    Args:
        expert_id: The expert's UUID
        file: The image file to upload
        db: Database session
        admin_data: Admin authentication data

    Returns:
        Dictionary containing the photo URL
    """
    # Validate file type
    content_type = file.content_type or ""
    filename = file.filename or ""
    if not is_allowed_file_type(content_type, filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed types: JPEG, PNG, GIF, WebP"
        )

    # Validate expert exists
    expert_service = ExpertService(db)
    expert = await expert_service.get_expert(uuid.UUID(expert_id))
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expert {expert_id} not found"
        )

    # Generate unique filename
    extension = get_file_extension(filename)
    unique_filename = f"expert_{expert_id}_{int(datetime.now().timestamp())}{extension}"
    file_path = UPLOAD_DIR / unique_filename

    # Save file
    try:
        content = await file.read()
        file_path.write_bytes(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        ) from e

    # Update expert's photo_url in database
    photo_url = f"/api/v1/uploads/expert-photo/{unique_filename}"
    expert.photo_url = photo_url
    await db.commit()
    await db.refresh(expert)

    return {
        "message": "Photo uploaded successfully",
        "expert_id": expert_id,
        "photo_url": photo_url,
        "filename": unique_filename
    }


@router.get(
    "/expert-photo/{filename}",
    response_class=FileResponse,
    summary="Get expert profile photo",
    description="Retrieve an expert's profile photo by filename"
)
async def get_expert_photo(
    filename: str,
):
    """Retrieve an expert's profile photo.

    Args:
        filename: The filename of the photo

    Returns:
        The image file
    """
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )

    # Determine media type from extension
    extension = get_file_extension(filename)
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    media_type = media_types.get(extension, "application/octet-stream")

    return FileResponse(file_path, media_type=media_type)


@router.delete(
    "/expert-photo/{filename}",
    status_code=status.HTTP_200_OK,
    summary="Delete expert profile photo",
    description="Delete an expert's profile photo"
)
async def delete_expert_photo(
    filename: str,
    expert_id: str,
    db: AsyncSession = Depends(get_db),
    admin_data: dict = Depends(require_admin_auth),
):
    """Delete an expert's profile photo.

    Args:
        filename: The filename of the photo to delete
        expert_id: The expert's UUID
        db: Database session
        admin_data: Admin authentication data

    Returns:
        Success message
    """
    # Delete file
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete file: {str(e)}"
            ) from e

    # Update expert's photo_url in database
    expert_service = ExpertService(db)
    expert = await expert_service.get_expert(uuid.UUID(expert_id))
    if expert:
        expert.photo_url = None
        await db.commit()
        await db.refresh(expert)

    return {
        "message": "Photo deleted successfully",
        "filename": filename,
        "expert_id": expert_id
    }
