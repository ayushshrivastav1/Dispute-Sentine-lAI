from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from backend.app.api.deps import get_db, get_current_user
from backend.app.models.dispute import Dispute

router = APIRouter()

@router.get("/")
async def list_review_queue(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    stmt = select(Dispute).where(
        or_(Dispute.status == "NEEDS_REVIEW", Dispute.status == "AWAITING_REVIEW")
    )
    result = await db.execute(stmt)
    disputes = result.scalars().all()
    
    formatted_data = []
    for d in disputes:
        formatted_data.append({
            "id": d.id,
            "orderAmount": d.amount if hasattr(d, 'amount') else (d.order_amount if hasattr(d, 'order_amount') else 10000),
            "currency": d.currency if hasattr(d, 'currency') else "INR",
            "reasonCode": d.reason if hasattr(d, 'reason') else "fraud",
            "winProbability": d.win_probability if hasattr(d, 'win_probability') else 50,
            "status": "escalated", # map NEEDS_REVIEW to escalated for frontend
            "merchantName": "Demo Merchant",
            "customerEmail": "customer@example.com",
            "gateway": "razorpay",
            "createdAt": d.created_at.isoformat() if hasattr(d, 'created_at') and d.created_at else "2026-08-28T09:12:00.000Z",
            "deadlineAt": d.deadline.isoformat() if hasattr(d, 'deadline') and d.deadline else "2026-09-06T09:12:00.000Z",
        })
        
    return {
        "items": formatted_data,
        "total": len(formatted_data),
        "page": 1,
        "pageSize": 50,
        "totalPages": 1
    }

@router.get("/{dispute_id}")
async def get_review_case(
    dispute_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    stmt = select(Dispute).where(Dispute.id == dispute_id)
    result = await db.execute(stmt)
    dispute = result.scalar_one_or_none()
    
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
        
    return dispute

@router.post("/{dispute_id}/submit")
async def submit_review_decision(
    dispute_id: str,
    action: str = Body(..., embed=True), # 'approve' or 'reject'
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    async with db.begin():
        stmt = select(Dispute).where(Dispute.id == dispute_id).with_for_update()
        result = await db.execute(stmt)
        dispute = result.scalar_one_or_none()
        
        if not dispute:
            raise HTTPException(status_code=404, detail="Dispute not found")
            
        if action == "approve":
            # Action logic: trigger contest via Razorpay SDK
            dispute.status = "CONTESTED"
            # TODO: append to audit ledger with hash chaining
        elif action == "reject":
            # Action logic: accept dispute
            dispute.status = "ACCEPTED"
            # TODO: append to audit ledger with hash chaining
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
            
    return {"message": f"Dispute {dispute_id} updated to {dispute.status}"}
