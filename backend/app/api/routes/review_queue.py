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
    return disputes

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
