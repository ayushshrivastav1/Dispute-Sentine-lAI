import logging
from fastapi import APIRouter, Request, Header, HTTPException, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.api.deps import get_db
from backend.app.core.config import settings
from backend.app.core.security import verify_webhook_signature
from backend.app.models.dispute import Dispute
from agent.graph.executor import run_dispute_pipeline

router = APIRouter()
logger = logging.getLogger(__name__)

async def process_dispute_background(dispute_id: str, payload: dict):
    logger.info(f"Starting agent pipeline for dispute {dispute_id}")
    try:
        await run_dispute_pipeline(dispute_id, payload)
        logger.info(f"Successfully completed agent pipeline for dispute {dispute_id}")
    except Exception as e:
        logger.error(f"Error in agent pipeline for dispute {dispute_id}: {str(e)}")

@router.post("/razorpay", status_code=202)
async def razorpay_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_razorpay_signature: str = Header(None),
    db: AsyncSession = Depends(get_db)
):
    if not x_razorpay_signature:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    raw_body = await request.body()
    
    is_valid = verify_webhook_signature(
        raw_body=raw_body, 
        signature=x_razorpay_signature, 
        secret=settings.RAZORPAY_WEBHOOK_SECRET
    )
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event_type = payload.get("event")
    
    if event_type == "dispute.created":
        dispute_data = payload.get("payload", {}).get("dispute", {}).get("entity", {})
        dispute_id = dispute_data.get("id")
        
        if not dispute_id:
            logger.warning("Dispute created event missing dispute id")
            return {"status": "ignored"}
            
        async with db.begin():
            # Check for existing dispute using FOR UPDATE for idempotency
            stmt = select(Dispute).where(Dispute.id == dispute_id).with_for_update()
            result = await db.execute(stmt)
            existing_dispute = result.scalar_one_or_none()
            
            if existing_dispute:
                logger.info(f"Dispute {dispute_id} already exists, skipping creation")
                return {"status": "already_processed"}
            
            # Create new dispute
            # Amounts are stored in paise
            # Razorpay dispute entity might not have order_id, mock it or extract if available
            new_dispute = Dispute(
                id=dispute_id,
                payment_id=dispute_data.get("payment_id", "unknown"),
                order_id=payload.get("payload", {}).get("payment", {}).get("entity", {}).get("order_id", "unknown"),
                amount=dispute_data.get("amount", 0),
                currency=dispute_data.get("currency", "INR"),
                status="OPEN",
                reason_code=dispute_data.get("reason_code", "unknown")
            )
            db.add(new_dispute)
            
        logger.info(f"Created new dispute record {dispute_id}")
        background_tasks.add_task(process_dispute_background, dispute_id, payload)
        
    return {"status": "received"}
