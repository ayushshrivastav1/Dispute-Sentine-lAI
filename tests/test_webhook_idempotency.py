import json
import hmac
import hashlib
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import settings

PAYLOAD = {
    "entity": "event",
    "account_id": "acc_test_123",
    "event": "payment.dispute.created",
    "contains": ["dispute"],
    "payload": {
        "dispute": {
            "entity": {
                "id": "disp_idemp_test_999",
                "payment_id": "pay_test_999",
                "amount": 149900,
                "currency": "INR",
                "reason_code": "fraud"
            }
        },
        "payment": {
            "entity": {
                "id": "pay_test_999",
                "order_id": "order_test_999"
            }
        }
    }
}

def test_duplicate_webhook_processed_once():
    event_id = "evt_idemp_test_unique_001"
    payload_bytes = json.dumps(PAYLOAD, separators=(',', ':')).encode("utf-8")
    signature = hmac.new(
        key=settings.RAZORPAY_WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()

    with TestClient(app) as client:
        with patch("backend.app.api.routes.webhooks.process_dispute_background") as mock_bg:
            # First Delivery
            first = client.post(
                "/api/v1/webhooks/razorpay",
                headers={
                    "x-razorpay-event-id": event_id,
                    "x-razorpay-signature": signature,
                    "content-type": "application/json"
                },
                content=payload_bytes,
            )

            # Second Delivery (Duplicate from Razorpay)
            second = client.post(
                "/api/v1/webhooks/razorpay",
                headers={
                    "x-razorpay-event-id": event_id,
                    "x-razorpay-signature": signature,
                    "content-type": "application/json"
                },
                content=payload_bytes,
            )

            assert first.status_code == 200
            assert second.status_code == 200

            # Verify duplicate event idempotency response
            assert second.json()["status"] == "already_processed"
            assert second.json()["event_id"] == event_id



