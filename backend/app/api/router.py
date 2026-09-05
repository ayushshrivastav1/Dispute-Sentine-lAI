from fastapi import APIRouter

from backend.app.api.routes import webhooks, disputes, review_queue, analytics, health, auth

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(disputes.router, prefix="/disputes", tags=["Disputes"])
api_router.include_router(review_queue.router, prefix="/review-queue", tags=["Review Queue"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

