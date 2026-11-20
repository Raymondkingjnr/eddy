from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db_session
from api.users.users import current_active_user

from models.models import User
from schemas import Stat
from api.stats import service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=Stat)
async def read_stats(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db_session),
) -> Stat:
    """Lesson statistics for the authenticated user only."""
    return await service.get_user_stats(session, user.id)
