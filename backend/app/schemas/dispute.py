from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DisputeCreate(BaseModel):
    dispute_id: str
    payment_id: str
    order_id: str
    amount: int
    currency: str = "INR"
    reason_code: str

class DisputeEvidenceSchema(BaseModel):
    id: str
    awb_code: Optional[str] = None
    carrier_name: Optional[str] = None
    signature_verified: bool = False
    ocr_confidence: Optional[float] = None
    
    class Config:
        from_attributes = True

class DisputeResponse(BaseModel):
    id: str
    payment_id: str
    order_id: str
    amount: int
    currency: str
    reason_code: str
    status: str
    win_probability: Optional[float] = None
    decision_route: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class DisputeListResponse(BaseModel):
    items: List[DisputeResponse]
    total: int

class DisputeDetailResponse(DisputeResponse):
    evidence: List[DisputeEvidenceSchema]
