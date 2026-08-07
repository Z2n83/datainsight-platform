"""
SQLAlchemy async engine and session configuration.
Supports MySQL (production) and SQLite (development fallback).
"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# Determine async driver from DATABASE_URL
def _get_async_url(url: str) -> str:
    """Convert sync MySQL URL to async if needed."""
    if "aiosqlite" in url or "aiomysql" in url or "asyncpg" in url:
        return url
    # Already contains async driver
    if "+" in url and any(d in url for d in ["aiosqlite", "aiomysql", "asyncpg"]):
        return url
    return url


async_database_url = _get_async_url(settings.DATABASE_URL)

# Create async engine
engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,
    future=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency: yield an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables. Call at application startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Dispose engine. Call at application shutdown."""
    await engine.dispose()
