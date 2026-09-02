from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ReviewSubmission(BaseModel):
    action: str  # approve or reject
    analyst_notes: Optional[str] = None
    modified_dossier: Optional[Dict[str, Any]] = None

class ReviewResponse(BaseModel):
    dispute_id: str
    action: str
    analyst_id: str
    timestamp: datetime
