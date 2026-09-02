from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.api.deps import get_db, get_current_user
from backend.app.models.dispute import Dispute

router = APIRouter()

@router.get("/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Total disputes
    total_stmt = select(func.count()).select_from(Dispute)
    total = await db.scalar(total_stmt) or 0
    
    # Contested disputes
    contested_stmt = select(func.count()).select_from(Dispute).where(Dispute.status == "CONTESTED")
    contested = await db.scalar(contested_stmt) or 0
    
    # Escalated disputes
    escalated_stmt = select(func.count()).select_from(Dispute).where(Dispute.status.in_(["NEEDS_REVIEW", "AWAITING_REVIEW"]))
    escalated = await db.scalar(escalated_stmt) or 0
    
    # Accepted disputes
    accepted_stmt = select(func.count()).select_from(Dispute).where(Dispute.status == "ACCEPTED")
    accepted = await db.scalar(accepted_stmt) or 0
    
    win_rate = 0.0 # Calculate win rate from history where applicable
    
    return {
        "total": total,
        "contested": contested,
        "escalated": escalated,
        "accepted": accepted,
        "win_rate": win_rate
    }

@router.get("/timeline")
async def get_analytics_timeline(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Assuming created_at is a DateTime field, extract date
    stmt = select(
        func.date(Dispute.created_at).label('date'), 
        func.count().label('count')
    ).group_by('date')
    
    result = await db.execute(stmt)
    
    timeline = [{"date": str(row.date), "count": row.count} for row in result.all()]
    
    return timeline
