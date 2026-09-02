import os

base_dir = r"C:\Users\lenovo\Desktop\dispute-sentinel-ai"

files = {
    r"backend\__init__.py": "",
    r"backend\app\__init__.py": "",
    r"backend\app\core\__init__.py": "",
    r"backend\app\db\__init__.py": "",
    r"backend\app\models\__init__.py": "from .dispute import Dispute\nfrom .evidence import DisputeEvidence\nfrom .audit_ledger import AuditLedger\n",
    r"backend\app\schemas\__init__.py": "",
    r"backend\app\api\__init__.py": "",
    r"backend\app\api\routes\__init__.py": "",
    
    r"backend\app\core\config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./dispute_sentinel.db"
    
    # Razorpay
    RAZORPAY_KEY_ID: str = "rzp_test_XXXXXXXXXXXX"
    RAZORPAY_KEY_SECRET: str = "XXXXXXXXXXXXXXXXXXXXXXXX"
    RAZORPAY_WEBHOOK_SECRET: str = "whsec_test"
    
    # LLM
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Auth
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    # App
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Policy Thresholds
    AUTO_CONTEST_THRESHOLD: float = 0.75
    AUTO_ACCEPT_THRESHOLD: float = 0.40
    MAX_AUTO_CONTEST_AMOUNT: int = 2500000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
""",
    r"backend\app\core\security.py": """import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from backend.app.core.config import settings

def verify_webhook_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    expected_sig = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, signature)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
""",
    r"backend\app\core\logging.py": """import logging
import json
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "trace_id": getattr(record, "trace_id", None),
            "dispute_id": getattr(record, "dispute_id", None),
            "event": getattr(record, "event", None),
        }
        return json.dumps({k: v for k, v in log_record.items() if v is not None})

def setup_logging(level: str = "INFO"):
    logger = logging.getLogger("dispute_sentinel")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    return logger
""",
    r"backend\app\db\base.py": """from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
""",
    r"backend\app\db\session.py": """from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

async def get_db():
    async with SessionLocal() as session:
        yield session
""",
    r"backend\app\db\immutability.py": """import hashlib
import json
from sqlalchemy.future import select
from backend.app.models.audit_ledger import AuditLedger

def compute_audit_hash(record_id, timestamp, dispute_id, action, payload_hash, previous_hash) -> str:
    data = f"{record_id}:{timestamp}:{dispute_id}:{action}:{payload_hash}:{previous_hash}"
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

async def append_audit_entry(db, dispute_id: str, action_type: str, actor_id: str, payload: dict) -> AuditLedger:
    payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()
    
    result = await db.execute(
        select(AuditLedger).order_by(AuditLedger.sequence_id.desc()).limit(1)
    )
    last_entry = result.scalars().first()
    previous_hash = last_entry.current_hash if last_entry else "GENESIS"
    
    entry = AuditLedger(
        dispute_id=dispute_id,
        action_type=action_type,
        actor_id=actor_id,
        payload_hash=payload_hash,
        previous_hash=previous_hash,
        current_hash="PENDING"
    )
    db.add(entry)
    await db.flush()
    
    entry.current_hash = compute_audit_hash(
        entry.sequence_id, 
        str(entry.created_at), 
        dispute_id, 
        action_type, 
        payload_hash, 
        previous_hash
    )
    return entry

async def verify_chain_integrity(db) -> tuple[bool, list[str]]:
    result = await db.execute(select(AuditLedger).order_by(AuditLedger.sequence_id.asc()))
    entries = result.scalars().all()
    
    if not entries:
        return True, []
        
    errors = []
    expected_prev_hash = "GENESIS"
    for entry in entries:
        if entry.previous_hash != expected_prev_hash:
            errors.append(f"Chain broken at sequence {entry.sequence_id}: prev_hash mismatch")
            
        computed_hash = compute_audit_hash(
            entry.sequence_id,
            str(entry.created_at),
            entry.dispute_id,
            entry.action_type,
            entry.payload_hash,
            entry.previous_hash
        )
        if entry.current_hash != computed_hash:
            errors.append(f"Chain broken at sequence {entry.sequence_id}: hash mismatch")
            
        expected_prev_hash = entry.current_hash
        
    return len(errors) == 0, errors
""",
    r"backend\app\models\dispute.py": """from sqlalchemy import String, BigInteger, Numeric, DateTime, func, Index
from sqlalchemy.orm import mapped_column, relationship
from backend.app.db.base import Base

class Dispute(Base):
    __tablename__ = "disputes"
    id = mapped_column(String(64), primary_key=True)  # disp_...
    payment_id = mapped_column(String(64), nullable=False)
    order_id = mapped_column(String(64), nullable=False)
    amount = mapped_column(BigInteger, nullable=False)  # paise
    currency = mapped_column(String(8), default="INR")
    reason_code = mapped_column(String(64), nullable=False)
    status = mapped_column(String(32), nullable=False)  # OPEN, CONTESTED, ACCEPTED, NEEDS_REVIEW
    win_probability = mapped_column(Numeric(4, 3), nullable=True)
    decision_route = mapped_column(String(32), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    evidence = relationship("DisputeEvidence", back_populates="dispute", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_disputes_status", "status"),
    )
""",
    r"backend\app\models\evidence.py": """from uuid import uuid4
from sqlalchemy import String, ForeignKey, DateTime, Boolean, Numeric, Text, JSON, func
from sqlalchemy.orm import mapped_column, relationship
from backend.app.db.base import Base

class DisputeEvidence(Base):
    __tablename__ = "dispute_evidence"
    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    dispute_id = mapped_column(String(64), ForeignKey("disputes.id", ondelete="CASCADE"))
    awb_code = mapped_column(String(64), nullable=True)
    carrier_name = mapped_column(String(64), nullable=True)
    delivery_timestamp = mapped_column(DateTime(timezone=True), nullable=True)
    pod_image_url = mapped_column(Text, nullable=True)
    signature_verified = mapped_column(Boolean, default=False)
    ocr_confidence = mapped_column(Numeric(4, 3), nullable=True)
    dossier_json = mapped_column(JSON, nullable=True)  # Use JSON for SQLite compat
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    dispute = relationship("Dispute", back_populates="evidence")
""",
    r"backend\app\models\audit_ledger.py": """from sqlalchemy import Integer, String, DateTime, func, Index
from sqlalchemy.orm import mapped_column
from backend.app.db.base import Base

class AuditLedger(Base):
    __tablename__ = "audit_ledger"
    sequence_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    dispute_id = mapped_column(String(64), nullable=False)
    action_type = mapped_column(String(64), nullable=False)
    actor_id = mapped_column(String(64), nullable=False)  # AGENT_POLICY_GATE | analyst user
    payload_hash = mapped_column(String(64), nullable=False)
    previous_hash = mapped_column(String(64), nullable=False)
    current_hash = mapped_column(String(64), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("idx_audit_dispute_id", "dispute_id"),
    )
""",
    r"backend\app\schemas\dispute.py": """from pydantic import BaseModel
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
""",
    r"backend\app\schemas\review.py": """from pydantic import BaseModel
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
""",
    r"backend\app\schemas\metrics.py": """from pydantic import BaseModel

class MetricsSummary(BaseModel):
    total_disputes: int
    auto_contested: int
    escalated: int
    auto_accepted: int
    win_rate: float
    total_amount_contested: int
    false_positive_count: int

class TimelineDataPoint(BaseModel):
    date: str
    count: int
    contested: int
    accepted: int
    escalated: int
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content or "# Init file\\n")
