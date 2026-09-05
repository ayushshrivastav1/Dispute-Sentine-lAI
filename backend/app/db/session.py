"""
DisputeSentinel AI — Async Database Engine & Session Factory

Creates the SQLAlchemy async engine and sessionmaker. Uses aiosqlite
for local development and asyncpg for PostgreSQL in production.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.app.core.config import settings

import os

# ── Engine Configuration ──────────────────────────────────
db_url = settings.DATABASE_URL
if (os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")) and db_url.startswith("sqlite"):
    db_url = "sqlite+aiosqlite:////tmp/dispute_sentinel.db"

connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    db_url,
    echo=settings.APP_DEBUG and settings.APP_ENV == "development",
    connect_args=connect_args,
)

# ── Session Factory ───────────────────────────────────────
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Dependency that yields an async database session.

    Usage in FastAPI:
        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
