"""
DisputeSentinel AI — Pydantic Validation Models for Dispute State

Provides runtime validation for intermediate node outputs, ensuring
data integrity as evidence flows through the LangGraph pipeline.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List


class ExtractedEvidenceModel(BaseModel):
    """Validated evidence gathered from order DB and carrier tracking."""

    order_id: str = Field(..., min_length=1, description="Internal order identifier")
    amount: int = Field(..., ge=0, description="Transaction amount in paise")
    currency: str = Field(default="INR", pattern=r"^[A-Z]{3}$")
    customer_name: str = Field(..., min_length=1)
    customer_email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    shipping_address: str = Field(..., min_length=1)
    billing_address: str = Field(default="")
    carrier_name: str = Field(..., min_length=1)
    awb_code: str = Field(..., min_length=1, description="Air Waybill / tracking code")
    delivery_status: str = Field(
        ...,
        description="DELIVERED | IN_TRANSIT | OUT_FOR_DELIVERY | RTO"
    )
    delivery_timestamp: Optional[str] = Field(
        default=None,
        description="ISO 8601 delivery confirmation timestamp"
    )
    delivery_gps: Optional[Dict[str, float]] = Field(
        default=None,
        description="GPS coordinates: {lat, lng}"
    )
    ip_address: str = Field(default="0.0.0.0")
    device_fingerprint: str = Field(default="unknown")
    successful_orders: int = Field(default=0, ge=0)
    prior_disputes: int = Field(default=0, ge=0)
    account_tenure_days: int = Field(default=0, ge=0)
    known_ip_addresses: List[str] = Field(default_factory=list)
    pod_image_url: Optional[str] = Field(default=None)

    @field_validator("delivery_status")
    @classmethod
    def validate_delivery_status(cls, v: str) -> str:
        valid = {"DELIVERED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "RTO", "UNKNOWN"}
        if v.upper() not in valid:
            raise ValueError(f"delivery_status must be one of {valid}, got '{v}'")
        return v.upper()


class VisionVerificationModel(BaseModel):
    """Validated vision OCR analysis results from PoD image."""

    pod_image_url: str = Field(default="")
    signature_detected: bool = Field(default=False)
    recipient_name_match: bool = Field(default=False)
    ocr_extracted_awb: str = Field(default="")
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Vision model confidence [0.0, 1.0]"
    )


class PolicyEvaluationModel(BaseModel):
    """Validated output from the deterministic policy gate."""

    s_delivery: float = Field(..., ge=0.0, le=1.0)
    s_signature: float = Field(..., ge=0.0, le=1.0)
    s_identity: float = Field(..., ge=0.0, le=1.0)
    s_risk: float = Field(..., ge=0.0, le=1.0)
    calculated_win_probability: float = Field(..., ge=0.0, le=1.0)
    decision_route: str = Field(
        ...,
        description="AUTO_CONTEST | ESCALATE_HUMAN | AUTO_ACCEPT"
    )
    reasoning: str = Field(default="", description="Human-readable decision explanation")

    @field_validator("decision_route")
    @classmethod
    def validate_decision_route(cls, v: str) -> str:
        valid = {"AUTO_CONTEST", "ESCALATE_HUMAN", "AUTO_ACCEPT"}
        if v not in valid:
            raise ValueError(f"decision_route must be one of {valid}, got '{v}'")
        return v
