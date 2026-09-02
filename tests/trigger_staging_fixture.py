import asyncio
import os
import sys
import json
import httpx
import hmac
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.app.core.config import settings

def generate_signature(payload: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

async def main():
    print("==================================================")
    print("STAGING FIXTURE: DISPUTE TRIGGER")
    print("==================================================")
    print("This script simulates a Razorpay webhook for a dispute.")
    print("It uses the 'pay_EFtmUsbwpXwBHI' payment which is seeded in the local DB.")
    
    # 1. Create a Razorpay-shaped webhook payload
    dispute_id = "disp_StagingFixt001"
    payment_id = "pay_EFtmUsbwpXwBHI" # from MOCK_ORDERS in db_client
    
    payload_dict = {
        "entity": "event",
        "account_id": "acc_XXXXXXXXXXXXX",
        "event": "payment.dispute.created",
        "contains": ["dispute", "payment"],
        "payload": {
            "dispute": {
                "entity": {
                    "id": dispute_id,
                    "entity": "dispute",
                    "payment_id": payment_id,
                    "amount": 500000,
                    "currency": "INR",
                    "reason_code": "goods_not_received",
                    "status": "open",
                    "phase": "chargeback"
                }
            },
            "payment": {
                "entity": {
                    "id": payment_id,
                    "order_id": "order_EKwxw5LRhOMZ"
                }
            }
        },
        "created_at": 1690000000
    }
    
    payload_str = json.dumps(payload_dict)
    
    # 2. Generate HMAC signature using the environment's webhook secret
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    signature = generate_signature(payload_str, secret)
    
    # 3. Post to local backend
    url = "http://localhost:8000/api/v1/webhooks/razorpay"
    
    print(f"\nSending webhook for {dispute_id} to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                content=payload_str,
                headers={
                    "Content-Type": "application/json",
                    "X-Razorpay-Signature": signature
                }
            )
            print(f"Response Status: {resp.status_code}")
            print(f"Response Body: {resp.text}")
            
            if resp.status_code == 202:
                print("\nSUCCESS: Webhook accepted. The LangGraph backend is now processing the dispute.")
                print("Check the backend console logs and the frontend UI.")
            else:
                print("\nFAILED: The backend did not accept the webhook.")
    except Exception as e:
        print(f"Error connecting to backend: {str(e)}")
        print("Make sure the backend is running (npm run dev:backend or python run.py)")

if __name__ == "__main__":
    asyncio.run(main())
