"""Image routes (GET, versions, regenerate)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.expression import Image
from app.models.user import User
from app.schemas.expression import ImageResponse

router = APIRouter(prefix="/api/v1/images", tags=["images"])


@router.get("/{expression_id}", response_model=ImageResponse)
async def get_active_image(
    expression_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """Get the active image for an expression."""
    result = await db.execute(
        select(Image).where(
            Image.expression_id == expression_id,
            Image.is_active == True,
        )
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active image for this expression")
    return image


@router.get("/{expression_id}/versions", response_model=list[ImageResponse])
async def list_image_versions(
    expression_id: str,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """List all image versions for an expression."""
    result = await db.execute(
        select(Image)
        .where(Image.expression_id == expression_id)
        .order_by(Image.version.desc())
    )
    return result.scalars().all()
