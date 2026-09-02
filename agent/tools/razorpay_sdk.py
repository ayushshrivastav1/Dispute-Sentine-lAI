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
        from backend.app.core.config import settings
        self.key_id = key_id or settings.RAZORPAY_KEY_ID
        self.key_secret = key_secret or settings.RAZORPAY_KEY_SECRET
        self.live_actions = settings.RAZORPAY_LIVE_ACTIONS
        self.upload_evidence = settings.RAZORPAY_UPLOAD_EVIDENCE
        self._auth = (self.key_id, self.key_secret)
        self._timeout = httpx.Timeout(REQUEST_TIMEOUT)

    async def fetch_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """Fetch dispute details from Razorpay."""
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(
                    f"{BASE_URL}/disputes/{dispute_id}",
                    auth=self._auth,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("HTTP Error fetching dispute %s: %s", dispute_id, str(e))
            raise

    async def contest_dispute(
        self, dispute_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Contest a dispute with compiled evidence."""
        if not self.live_actions:
            logger.info("[SAFE MODE] SKIPPED PATCH /v1/disputes/%s/contest", dispute_id)
            return {
                "id": dispute_id,
                "action": "AUTO_CONTEST",
                "execution": "SKIPPED_SAFE_MODE",
                "live_action": False,
                "reason": "RAZORPAY_LIVE_ACTIONS=false"
            }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.patch(
                    f"{BASE_URL}/disputes/{dispute_id}/contest",
                    json=payload,
                    auth=self._auth,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("HTTP Error contesting dispute %s: %s", dispute_id, str(e))
            raise

    async def accept_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """Accept a dispute (concede the chargeback)."""
        if not self.live_actions:
            logger.info("[SAFE MODE] SKIPPED POST /v1/disputes/%s/accept", dispute_id)
            return {
                "id": dispute_id,
                "action": "AUTO_ACCEPT",
                "execution": "SKIPPED_SAFE_MODE",
                "live_action": False,
                "reason": "RAZORPAY_LIVE_ACTIONS=false"
            }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{BASE_URL}/disputes/{dispute_id}/accept",
                    auth=self._auth,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("HTTP Error accepting dispute %s: %s", dispute_id, str(e))
            raise

    async def upload_document(
        self, file_bytes: bytes, filename: str
    ) -> Dict[str, Any]:
        """Upload an evidence document to Razorpay."""
        if not self.upload_evidence:
            logger.info("[SAFE MODE] SKIPPED Document Upload for %s", filename)
            return {
                "id": "doc_skipped_safe_mode",
                "action": "UPLOAD_DOCUMENT",
                "execution": "SKIPPED_SAFE_MODE",
                "live_action": False,
                "reason": "RAZORPAY_UPLOAD_EVIDENCE=false"
            }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{BASE_URL}/documents",
                    files={"file": (filename, file_bytes)},
                    data={"purpose": "dispute_evidence"},
                    auth=self._auth,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error("HTTP Error uploading document %s: %s", filename, str(e))
            raise
