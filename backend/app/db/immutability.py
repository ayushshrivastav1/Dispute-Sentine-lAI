"""
DisputeSentinel AI — Cryptographic Audit Ledger

Implements append-only SHA-256 hash-chained audit logging for
non-repudiation of all financial and automated decisions.

Each record is linked to the previous via:
  Hash_n = SHA-256(record_id || timestamp || dispute_id || action || payload_hash || hash_{n-1})
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.audit_ledger import AuditLedger

logger = logging.getLogger(__name__)

# Genesis hash for the first entry in the chain
GENESIS_HASH = "0" * 64


def compute_payload_hash(payload: Any) -> str:
    """Compute SHA-256 hash of a payload (dict, string, or bytes).

    Args:
        payload: The data to hash.

    Returns:
        Hex-encoded SHA-256 digest.
    """
    if isinstance(payload, dict):
        serialized = json.dumps(payload, sort_keys=True, default=str)
    elif isinstance(payload, bytes):
        serialized = payload.decode("utf-8", errors="replace")
    else:
        serialized = str(payload)

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def compute_audit_hash(
    record_id: int,
    timestamp: str,
    dispute_id: str,
    action: str,
    payload_hash: str,
    previous_hash: str,
) -> str:
    """Compute the rolling SHA-256 hash for an audit entry.

    Args:
        record_id: Sequential ID of this audit record.
        timestamp: ISO 8601 timestamp string.
        dispute_id: Razorpay dispute identifier.
        action: Action type (e.g., 'AUTO_CONTEST', 'ESCALATE_HUMAN').
        payload_hash: SHA-256 hash of the action payload.
        previous_hash: Hash of the preceding audit entry.

    Returns:
        Hex-encoded SHA-256 hash linking this entry to the chain.
    """
    data = f"{record_id}||{timestamp}||{dispute_id}||{action}||{payload_hash}||{previous_hash}"
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


async def get_previous_hash(db: AsyncSession) -> str:
    """Retrieve the hash of the most recent audit entry.

    Returns GENESIS_HASH if the ledger is empty.
    """
    result = await db.execute(
        select(AuditLedger.current_hash)
        .order_by(AuditLedger.sequence_id.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    return row if row else GENESIS_HASH


async def append_audit_entry(
    db: AsyncSession,
    dispute_id: str,
    action_type: str,
    actor_id: str,
    payload: Any,
) -> AuditLedger:
    """Append a new entry to the immutable audit ledger.

    Computes the rolling hash chain and persists the record.

    Args:
        db: Async database session.
        dispute_id: Razorpay dispute identifier.
        action_type: Action performed (e.g., 'AUTO_CONTEST').
        actor_id: Who performed it ('AGENT_POLICY_GATE' or analyst ID).
        payload: The action payload (dict, dossier, etc.).

    Returns:
        The created AuditLedger record.
    """
    previous_hash = await get_previous_hash(db)
    payload_hash = compute_payload_hash(payload)
    timestamp = datetime.now(timezone.utc).isoformat()

    # We need to predict the sequence_id for hash computation
    # Use a temporary placeholder then update after insert
    result = await db.execute(
        select(AuditLedger.sequence_id)
        .order_by(AuditLedger.sequence_id.desc())
        .limit(1)
    )
    last_id = result.scalar_one_or_none() or 0
    next_id = last_id + 1

    current_hash = compute_audit_hash(
        record_id=next_id,
        timestamp=timestamp,
        dispute_id=dispute_id,
        action=action_type,
        payload_hash=payload_hash,
        previous_hash=previous_hash,
    )

    entry = AuditLedger(
        dispute_id=dispute_id,
        action_type=action_type,
        actor_id=actor_id,
        payload_hash=payload_hash,
        previous_hash=previous_hash,
        current_hash=current_hash,
    )

    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    logger.info(
        "Audit entry appended: seq=%d dispute=%s action=%s hash=%s",
        entry.sequence_id,
        dispute_id,
        action_type,
        current_hash[:16] + "...",
    )

    return entry


async def verify_chain_integrity(db: AsyncSession) -> tuple[bool, list[str]]:
    """Verify the entire audit ledger hash chain.

    Walks through all entries sequentially, recomputing each hash
    and comparing against the stored value. Any mismatch indicates
    data tampering.

    Returns:
        Tuple of (is_valid, list_of_error_messages).
    """
    result = await db.execute(
        select(AuditLedger).order_by(AuditLedger.sequence_id.asc())
    )
    entries = result.scalars().all()
    errors: list[str] = []

    if not entries:
        return True, []

    expected_previous = GENESIS_HASH

    for entry in entries:
        # Verify previous_hash linkage
        if entry.previous_hash != expected_previous:
            errors.append(
                f"Chain break at seq={entry.sequence_id}: "
                f"expected previous_hash={expected_previous[:16]}..., "
                f"got={entry.previous_hash[:16]}..."
            )

        # Recompute the current hash
        recomputed = compute_audit_hash(
            record_id=entry.sequence_id,
            timestamp=entry.created_at.isoformat() if entry.created_at else "",
            dispute_id=entry.dispute_id,
            action=entry.action_type,
            payload_hash=entry.payload_hash,
            previous_hash=entry.previous_hash,
        )

        if entry.current_hash != recomputed:
            errors.append(
                f"Hash mismatch at seq={entry.sequence_id}: "
                f"stored={entry.current_hash[:16]}..., "
                f"computed={recomputed[:16]}..."
            )

        expected_previous = entry.current_hash

    is_valid = len(errors) == 0

    if is_valid:
        logger.info("Audit chain integrity verified: %d entries, all valid", len(entries))
    else:
        logger.error("Audit chain integrity FAILED: %d errors found", len(errors))

    return is_valid, errors
