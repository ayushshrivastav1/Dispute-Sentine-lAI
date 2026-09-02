import asyncio
import os
import sys

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.config import settings
from agent.tools.razorpay_sdk import RazorpayClient
import httpx

async def main():
    print("==================================================")
    print("RAZORPAY INTEGRATION TEST (READ-ONLY)")
    print("==================================================")
    
    if settings.RAZORPAY_KEY_ID.startswith("rzp_test_XXXX"):
        print("ERROR: Default mock credentials detected in environment.")
        print("Please configure real RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in your .env file.")
        return

    print("Credentials loaded successfully (hidden).")
    print("Fetching live disputes from Razorpay (GET /v1/disputes)...\n")
    
    try:
        # Use direct httpx to query the list (since RazorpayClient doesn't have a fetch_all_disputes yet)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.razorpay.com/v1/disputes",
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
            print(f"HTTP Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                count = data.get("count", len(items))
                
                print(f"Number of disputes retrieved: {count}")
                print("\nDisputes Metadata:")
                for i, d in enumerate(items[:5]): # show first 5
                    print(f"  {i+1}. ID: {d.get('id')} | Amount: {d.get('amount')/100} {d.get('currency')} | Reason: {d.get('reason_code')} | Status: {d.get('status')}")
                if count > 5:
                    print(f"  ...and {count - 5} more.")
            else:
                print(f"API Error Response: {resp.text}")

    except httpx.HTTPError as e:
        print(f"HTTP Request failed: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
