"""
DisputeSentinel AI — Razorpay Contest Payload Schema

Strict Pydantic model matching the Razorpay PATCH /v1/disputes/{id}/contest
API specification. All generated dossiers are validated against this schema
before submission, ensuring API compatibility.

Reference: https://razorpay.com/docs/api/disputes/contest
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class EvidenceDocument(BaseModel):
    """Custom evidence type with associated document IDs."""

    type: str = Field(
        ...,
        min_length=1,
        description="Evidence category (e.g., 'receipt_signed_by_customer')"
    )
    document_ids: List[str] = Field(
        ...,
        min_length=1,
        description="List of Razorpay document IDs (doc_...)"
    )

    @field_validator("document_ids")
    @classmethod
    def validate_document_ids(cls, v: List[str]) -> List[str]:
        for doc_id in v:
            if not doc_id.startswith("doc_"):
                raise ValueError(f"Document ID must start with 'doc_', got '{doc_id}'")
        return v


class RazorpayContestPayload(BaseModel):
    """Validated payload for Razorpay dispute contest submission.

    Matches the PATCH /v1/disputes/{id}/contest API specification exactly.
    """

    action: str = Field(
        default="submit",
        description="'draft' to save without submitting, 'submit' to send to bank"
    )
    amount: Optional[int] = Field(
        default=None,
        ge=0,
        description="Amount to contest in paise. Defaults to full dispute amount."
    )
    summary: str = Field(
        ...,
        max_length=1000,
        description="Factual evidence summary for the bank (max 1000 chars)"
    )
    shipping_proof: Optional[List[str]] = Field(
        default=None,
        description="Document IDs for shipping/delivery proof"
    )
    billing_proof: Optional[List[str]] = Field(
        default=None,
        description="Document IDs for billing/invoice proof"
    )
    cancellation_policy: Optional[List[str]] = Field(
        default=None,
        description="Document IDs for cancellation/refund policy"
    )
    customer_communication: Optional[List[str]] = Field(
        default=None,
        description="Document IDs for customer communication transcripts"
    )
    proof_of_service: Optional[List[str]] = Field(
        default=None,
        description="Document IDs for proof of service delivery"
    )
    explanation_file: Optional[List[str]] = Field(
        default=None,
        description="Document IDs for written explanation"
    )
    others: Optional[List[EvidenceDocument]] = Field(
        default=None,
        description="Additional custom evidence types"
    )

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ("draft", "submit"):
            raise ValueError(f"action must be 'draft' or 'submit', got '{v}'")
        return v

    def to_api_payload(self) -> dict:
        """Convert to the exact JSON structure expected by Razorpay API.

        Excludes None fields to produce a clean payload.
        """
        payload = {}
        payload["action"] = self.action

        if self.amount is not None:
            payload["amount"] = self.amount
        if self.summary:
            payload["summary"] = self.summary
        if self.shipping_proof:
            payload["shipping_proof"] = self.shipping_proof
        if self.billing_proof:
            payload["billing_proof"] = self.billing_proof
        if self.cancellation_policy:
            payload["cancellation_policy"] = self.cancellation_policy
        if self.customer_communication:
            payload["customer_communication"] = self.customer_communication
        if self.proof_of_service:
            payload["proof_of_service"] = self.proof_of_service
        if self.explanation_file:
            payload["explanation_file"] = self.explanation_file
        if self.others:
            payload["others"] = [
                {"type": e.type, "document_ids": e.document_ids}
                for e in self.others
            ]

        return payload
