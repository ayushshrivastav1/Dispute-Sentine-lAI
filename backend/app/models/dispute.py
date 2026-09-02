"""
DisputeSentinel AI — Dispute ORM Model

Core disputes lifecycle table storing payment identifiers,
contest status, win probability, and decision routing.
"""

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class Dispute(Base):
    """Dispute case entity tracking the full chargeback lifecycle."""

    __tablename__ = "disputes"

    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, comment="e.g., disp_O123456789ABCD"
    )
    payment_id: Mapped[str] = mapped_column(String(64), nullable=False)
    order_id: Mapped[str] = mapped_column(String(64), nullable=False)
    amount: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="Amount in paise (INR × 100)"
    )
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="OPEN",
        comment="OPEN | CONTESTED | ACCEPTED | NEEDS_REVIEW",
    )
    win_probability: Mapped[float | None] = mapped_column(
        Numeric(4, 3), nullable=True
    )
    decision_route: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="AUTO_CONTEST | ESCALATE_HUMAN | AUTO_ACCEPT",
    )
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship to evidence records
    evidence = relationship(
        "DisputeEvidence",
        back_populates="dispute",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_disputes_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Dispute id={self.id} status={self.status} amount={self.amount}>"
