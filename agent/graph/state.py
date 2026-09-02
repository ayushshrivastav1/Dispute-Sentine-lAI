"""
DisputeSentinel AI — Graph State Schema

Defines the shared memory model (TypedDict) used by all LangGraph nodes.
Each node reads from and writes to this state, enabling a typed,
validated data flow through the entire dispute resolution pipeline.
"""

from typing import TypedDict, List, Optional, Dict, Any, Annotated
import operator


class ExtractedEvidence(TypedDict):
    """Evidence gathered from internal databases and carrier tracking APIs.

    Populated by the Evidence Extractor node (Node 1).
    """
    order_id: str
    amount: int                          # In paise (INR × 100)
    currency: str
    customer_name: str
    customer_email: str
    shipping_address: str
    billing_address: str
    carrier_name: str
    awb_code: str
    delivery_status: str                 # DELIVERED | IN_TRANSIT | OUT_FOR_DELIVERY | RTO
    delivery_timestamp: Optional[str]    # ISO 8601
    delivery_gps: Optional[Dict[str, float]]  # {"lat": ..., "lng": ...}
    ip_address: str
    device_fingerprint: str
    # Customer history metrics (for identity & risk scoring)
    successful_orders: int
    prior_disputes: int
    account_tenure_days: int
    known_ip_addresses: List[str]
    pod_image_url: Optional[str]


class VisionVerification(TypedDict):
    """Results from multi-modal vision OCR analysis of Proof of Delivery.

    Populated by the Vision OCR node (Node 2).
    """
    pod_image_url: str
    signature_detected: bool
    recipient_name_match: bool
    ocr_extracted_awb: str
    confidence_score: float              # [0.0, 1.0]


class DisputeState(TypedDict):
    """Central shared state for the LangGraph dispute resolution pipeline.

    All nodes read from and write to this TypedDict. Fields are populated
    progressively as the state machine traverses through extraction,
    verification, policy evaluation, and action execution.
    """
    # ── Core Dispute Identifiers ──────────────────────────
    dispute_id: str
    payment_id: str
    dispute_reason: str
    dispute_amount: int                  # In paise (INR × 100)
    due_by: int                          # Unix timestamp
    raw_webhook_payload: Dict[str, Any]

    # ── Node 1: Evidence Extractor Output ─────────────────
    evidence: Optional[ExtractedEvidence]

    # ── Node 2: Vision OCR Output ─────────────────────────
    vision: Optional[VisionVerification]

    # ── Node 3: Policy Gate Output ────────────────────────
    calculated_win_probability: float
    decision_route: str                  # "AUTO_CONTEST" | "ESCALATE_HUMAN" | "AUTO_ACCEPT"

    # ── Node 4A/4B: Action Output ─────────────────────────
    formatted_dossier: Optional[Dict[str, Any]]
    submission_status: str               # "PENDING" | "SUBMITTED" | "AWAITING_REVIEW" | "ACCEPTED" | "FAILED"

    # ── Error Tracking (Accumulated via reducer) ──────────
    error_log: Annotated[List[str], operator.add]

    # ── Audit Chain ───────────────────────────────────────
    audit_hash: Optional[str]
