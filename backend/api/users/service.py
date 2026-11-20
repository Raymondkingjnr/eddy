from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.models import User


async def list_users(session: AsyncSession, *, skip: int, limit: int) -> list[User]:
    result = await session.scalars(
        select(User)
        .where(User.is_active.is_(True))
        .order_by(User.fullname, User.id)
        .offset(skip)
        .limit(limit)
    )
    return list(result)
