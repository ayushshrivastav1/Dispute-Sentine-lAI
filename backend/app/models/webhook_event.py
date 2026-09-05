from sqlalchemy import Column, String, DateTime
from datetime import datetime

from backend.app.db.base import Base

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    event_id = Column(String(128), primary_key=True, unique=True, nullable=False, index=True)
    event_type = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
