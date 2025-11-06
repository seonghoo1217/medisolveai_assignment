from collections.abc import AsyncIterator
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from Assignment1.app.core.config import get_settings


settings = get_settings()

engine = create_async_engine(
    settings.sqlalchemy_dsn,
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=False,
    future=True,
)

AsyncSessionFactory = async_sessionmaker(
    engine, expire_on_commit=False, autoflush=False, future=True
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = AsyncSessionFactory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def session_scope() -> AsyncIterator[AsyncSession]:
    """Context manager utility for scripts."""
    session = AsyncSessionFactory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
