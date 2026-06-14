"""User settings routes."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserSettings
from app.schemas.auth import UserSettingsResponse, UserSettingsUpdate

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me/settings", response_model=UserSettingsResponse)
async def get_settings(current_user: User = Depends(get_current_user)):
    """Return current user's settings."""
    return current_user.settings


@router.put("/me/settings", response_model=UserSettingsResponse)
async def update_settings(
    body: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user settings (partial update)."""
    settings = current_user.settings
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    await db.flush()
    await db.refresh(settings)
    return settings
