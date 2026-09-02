"""
DisputeSentinel AI — Evidence ORM Model

Normalized table storing raw evidence, OCR results, carrier
tracking data, and the compiled contest dossier JSON.
"""

from uuid import uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class DisputeEvidence(Base):
    """Gathered evidence record linked to a dispute case."""

    __tablename__ = "dispute_evidence"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    dispute_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("disputes.id", ondelete="CASCADE"),
        nullable=False,
    )
    awb_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    carrier_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    delivery_timestamp = mapped_column(DateTime(timezone=True), nullable=True)
    pod_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    signature_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    ocr_confidence: Mapped[float | None] = mapped_column(
        Numeric(4, 3), nullable=True
    )
    dossier_json = mapped_column(
        JSON, nullable=True, comment="Compiled contest dossier"
    )
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Back-reference to parent dispute
    dispute = relationship("Dispute", back_populates="evidence")

    def __repr__(self) -> str:
        return f"<DisputeEvidence id={self.id} dispute={self.dispute_id}>"
