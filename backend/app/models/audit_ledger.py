"""
DisputeSentinel AI — Audit Ledger ORM Model

Append-only, cryptographically linked table recording every
action taken on every dispute. Each entry's hash depends on
the previous entry, forming an unbreakable chain.
"""

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class AuditLedger(Base):
    """Immutable audit trail entry with SHA-256 hash chaining."""

    __tablename__ = "audit_ledger"

    sequence_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    dispute_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="e.g., AUTO_CONTEST, ESCALATE_HUMAN, ANALYST_APPROVE",
    )
    actor_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="AGENT_POLICY_GATE | AGENT_CONTEST | analyst user ID",
    )
    payload_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="SHA-256 of the action payload/dossier",
    )
    previous_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Hash of the previous audit entry (chain link)",
    )
    current_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="Rolling SHA-256 hash for this entry",
    )
    created_at = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("idx_audit_dispute_id", "dispute_id"),
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLedger seq={self.sequence_id} "
            f"dispute={self.dispute_id} action={self.action_type}>"
        )
