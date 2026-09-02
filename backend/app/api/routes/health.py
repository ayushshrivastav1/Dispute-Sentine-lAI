from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api.deps import get_db

router = APIRouter()

@router.get("/health/live")
async def live():
    return {"status": "alive"}

@router.get("/health/ready")
async def ready(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not ready", "database": "disconnected", "error": str(e)}

@router.get("/health/integrations")
async def integrations(db: AsyncSession = Depends(get_db)):
    from backend.app.core.config import settings
    from agent.tools.razorpay_sdk import RazorpayClient
    import httpx
    
    # Check DB
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        
    # Check Razorpay connectivity
    rzp_connectivity = "disconnected"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get("https://api.razorpay.com/v1/disputes", auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            if resp.status_code in (200, 401): # 401 means reached but invalid key, 200 means success
                rzp_connectivity = "connected" if resp.status_code == 200 else "invalid_credentials"
    except Exception:
        pass

    return {
        "database": db_status,
        "razorpay": {
            "credentials_configured": settings.RAZORPAY_KEY_ID != "rzp_test_XXXXXXXXXXXX",
            "api_connectivity": rzp_connectivity,
            "live_actions_enabled": settings.RAZORPAY_LIVE_ACTIONS,
            "evidence_upload_enabled": settings.RAZORPAY_UPLOAD_EVIDENCE
        },
        "llm": {
            "provider": settings.LLM_PROVIDER,
            "configured": settings.GROQ_API_KEY != "gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" if settings.LLM_PROVIDER == "groq" else settings.OPENAI_API_KEY != "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        },
        "carrier": {
            "provider": settings.CARRIER_PROVIDER,
            "configured": bool(settings.CARRIER_API_KEY) if settings.CARRIER_PROVIDER != "demo" else True
        }
    }
