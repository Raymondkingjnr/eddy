from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db import get_db_session
from models.models import User
from schemas import UserDirectoryRead
from api.users.service import list_users
from api.users.users import current_active_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserDirectoryRead])
async def get_users(
    _: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[User]:
    return await list_users(session, skip=skip, limit=limit)
