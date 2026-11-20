from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from collections.abc import AsyncGenerator
from fastapi_users.db import SQLAlchemyUserDatabase
from models.models import Base, User
from fastapi import Depends
from config.config import settings
from config.db_config import database_url_for_engine

database_url = database_url_for_engine(settings.DATABASE_URL)
is_sqlite = database_url.startswith("sqlite")


def enable_sqlite_foreign_keys(sync_engine) -> None:
    """SQLite ignores ON DELETE CASCADE unless foreign keys are switched on
    for every connection; the models rely on it (passive_deletes=True)."""
    @event.listens_for(sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


engine = create_async_engine(database_url,
                             pool_pre_ping=True,
                             pool_recycle=300,
                             echo=True
                             )

if is_sqlite:
    enable_sqlite_foreign_keys(engine.sync_engine)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    yield SQLAlchemyUserDatabase(session, User)
