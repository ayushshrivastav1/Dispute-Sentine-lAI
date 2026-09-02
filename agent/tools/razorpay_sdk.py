"""
DisputeSentinel AI — Razorpay REST Client

Official Razorpay API wrapper for dispute operations:
- Fetch dispute details (GET /v1/disputes/{id})
- Contest a dispute (PATCH /v1/disputes/{id}/contest)
- Accept a dispute (POST /v1/disputes/{id}/accept)
- Upload evidence documents (POST /v1/documents)

Uses httpx.AsyncClient with Basic Auth. Automatically switches to
mock responses when the API key starts with 'rzp_test_XXXX'.
"""

import os
import logging
from typing import Dict, Any, Optional

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://api.razorpay.com/v1"
REQUEST_TIMEOUT = 5.0  # seconds


class RazorpayClient:
    """Async HTTP client for Razorpay Disputes API."""

    def __init__(
        self,
        key_id: Optional[str] = None,
        key_secret: Optional[str] = None,
    ):
        self.key_id = key_id or os.environ.get("RAZORPAY_KEY_ID", "rzp_test_XXXXXXXXXXXX")
        self.key_secret = key_secret or os.environ.get("RAZORPAY_KEY_SECRET", "XXXXXXXXXXXXXXXXXXXXXXXX")
        self.is_demo = self.key_id.startswith("rzp_test_XXXX")
        self._auth = (self.key_id, self.key_secret)
        self._timeout = httpx.Timeout(REQUEST_TIMEOUT)

    async def fetch_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """Fetch dispute details from Razorpay.

        Args:
            dispute_id: Razorpay dispute ID (disp_...).

        Returns:
            Dispute entity with metadata, status, and respond_by deadline.
        """
        if self.is_demo:
            logger.info("[DEMO] Simulating GET /v1/disputes/%s", dispute_id)
            return {
                "id": dispute_id,
                "entity": "dispute",
                "payment_id": "pay_EFtmUsbwpXwBHI",
                "amount": 500000,
                "currency": "INR",
                "amount_deducted": 500000,
                "reason_code": "goods_not_received",
                "reason_description": "Customer claims goods were not received",
                "status": "open",
                "phase": "chargeback",
                "respond_by": 1690604800,
                "created_at": 1690000500,
            }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(
                f"{BASE_URL}/disputes/{dispute_id}",
                auth=self._auth,
            )
            response.raise_for_status()
            return response.json()

    async def contest_dispute(
        self, dispute_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Contest a dispute with compiled evidence.

        Args:
            dispute_id: Razorpay dispute ID (disp_...).
            payload: Contest evidence payload matching Razorpay spec.

        Returns:
            Updated dispute entity with status 'under_review'.
        """
        if self.is_demo:
            logger.info("[DEMO] Simulating PATCH /v1/disputes/%s/contest", dispute_id)
            return {
                "id": dispute_id,
                "entity": "dispute",
                "status": "under_review",
                "phase": "chargeback",
            }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.patch(
                f"{BASE_URL}/disputes/{dispute_id}/contest",
                json=payload,
                auth=self._auth,
            )
            response.raise_for_status()
            return response.json()

    async def accept_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """Accept a dispute (concede the chargeback).

        This action is irreversible. The dispute status transitions to 'lost'
        and the dispute amount is deducted from the merchant's account.

        Args:
            dispute_id: Razorpay dispute ID (disp_...).

        Returns:
            Updated dispute entity with status 'lost'.
        """
        if self.is_demo:
            logger.info("[DEMO] Simulating POST /v1/disputes/%s/accept", dispute_id)
            return {
                "id": dispute_id,
                "entity": "dispute",
                "status": "lost",
            }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{BASE_URL}/disputes/{dispute_id}/accept",
                auth=self._auth,
            )
            response.raise_for_status()
            return response.json()

    async def upload_document(
        self, file_bytes: bytes, filename: str
    ) -> Dict[str, Any]:
        """Upload an evidence document to Razorpay.

        Args:
            file_bytes: Raw binary content of the file.
            filename: Original filename with extension.

        Returns:
            Document entity with Razorpay document ID (doc_...).
        """
        if self.is_demo:
            logger.info("[DEMO] Simulating POST /v1/documents for %s", filename)
            return {
                "id": "doc_EFtmUsbwpXwBH9",
                "entity": "document",
                "purpose": "dispute_evidence",
                "name": filename,
                "mime_type": "application/pdf",
            }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(
                f"{BASE_URL}/documents",
                files={"file": (filename, file_bytes)},
                data={"purpose": "dispute_evidence"},
                auth=self._auth,
            )
            response.raise_for_status()
            return response.json()
