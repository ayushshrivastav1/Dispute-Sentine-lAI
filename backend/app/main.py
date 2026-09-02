from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging
from backend.app.api.router import api_router
from backend.app.db.session import engine
from backend.app.db.base import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    setup_logging(settings.LOG_LEVEL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose engine
    await engine.dispose()

app = FastAPI(
    title="DisputeSentinel AI",
    description="Autonomous Dispute Defense & Risk Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router, prefix="/api/v1")
