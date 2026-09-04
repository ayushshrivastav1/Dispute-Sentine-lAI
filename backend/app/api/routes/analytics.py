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
    
    win_rate = 82.4 # Mocked for demo, or calculate
    
    return {
        "totalContestedCapital": 145200000,
        "contestedCapitalChangePct": 12,
        "winRate": win_rate,
        "winRateTarget": 75,
        "falsePositiveCost": 1240000,
        "falsePositiveCases": 6,
        "activeEscalations": escalated,
        "trend": [
            { "month": "Mar", "contested": 82400000, "recovered": 61300000 },
            { "month": "Apr", "contested": 96100000, "recovered": 74800000 },
            { "month": "May", "contested": 88700000, "recovered": 70100000 },
            { "month": "Jun", "contested": 114500000, "recovered": 92600000 },
            { "month": "Jul", "contested": 129800000, "recovered": 106400000 },
            { "month": "Aug", "contested": 145200000, "recovered": 119600000 }
        ],
        "statusBreakdown": [
            { "status": "auto_contested", "label": "Auto-Contested", "count": 148 },
            { "status": "escalated", "label": "Escalated", "count": escalated },
            { "status": "won", "label": "Won", "count": 96 },
            { "status": "accepted_loss", "label": "Accepted Loss", "count": 23 },
            { "status": "pending_evidence", "label": "Pending Evidence", "count": 17 }
        ]
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
