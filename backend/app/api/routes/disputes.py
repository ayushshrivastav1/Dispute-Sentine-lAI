from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from backend.app.api.deps import get_db, get_current_user
from backend.app.models.dispute import Dispute
from agent.graph.executor import run_dispute_pipeline

router = APIRouter()

@router.get("/")
async def list_disputes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    stmt = select(Dispute).offset(skip).limit(limit)
    if status:
        stmt = stmt.where(Dispute.status == status)
        
    result = await db.execute(stmt)
    disputes = result.scalars().all()
    return disputes

@router.get("/{dispute_id}")
async def get_dispute(
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

@router.post("/{dispute_id}/trigger")
async def trigger_dispute_pipeline(
    dispute_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    stmt = select(Dispute).where(Dispute.id == dispute_id)
    result = await db.execute(stmt)
    dispute = result.scalar_one_or_none()
    
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")
        
    async def run_pipeline(d_id: str):
        try:
            await run_dispute_pipeline(d_id)
        except Exception as e:
            pass # Handle error appropriately in real logic
            
    background_tasks.add_task(run_pipeline, dispute_id)
    
    return {"message": "Pipeline manually triggered in background", "dispute_id": dispute_id}
