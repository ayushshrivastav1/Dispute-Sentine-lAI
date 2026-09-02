"""
DisputeSentinel AI — Carrier Tracking Integration

Provides shipment tracking via logistics provider APIs (Delhivery,
BlueDart, Ecom Express). Uses mock data in demo mode with realistic
Indian e-commerce delivery timelines.
"""

import asyncio
from typing import Dict, Any, List
from agent.tools.registry import tool_handler


import asyncio
import os
from typing import Dict, Any, Protocol
from agent.tools.registry import tool_handler

class CarrierProvider(Protocol):
    async def track_shipment(self, awb_code: str, carrier_name: str) -> Dict[str, Any]:
        ...

class DemoCarrierProvider:
    MOCK_TRACKING: Dict[str, Dict[str, Any]] = {
        "AWB123456789": {
            "carrier": "delhivery",
            "status": "DELIVERED",
            "events": [
                {"timestamp": "2024-01-16T10:00:00Z", "location": "Bangalore Hub", "description": "Shipment picked up"},
                {"timestamp": "2024-01-17T14:45:00Z", "location": "123 MG Road, Bangalore", "description": "Delivered - Signed by RAJESH"},
            ],
            "delivery_timestamp": "2024-01-17T14:45:00Z",
            "delivery_gps": {"lat": 12.9716, "lng": 77.5946},
            # A real placeholder image that OpenAI Vision can fetch
            "pod_image_url": "https://upload.wikimedia.org/wikipedia/commons/3/30/George_Washington_signature.svg", 
        },
        "AWB987654321": {
            "carrier": "bluedart",
            "status": "IN_TRANSIT",
            "events": [
                {"timestamp": "2024-02-21T09:00:00Z", "location": "Kolkata Hub", "description": "Shipment picked up"},
            ],
            "delivery_timestamp": None,
            "delivery_gps": None,
            "pod_image_url": None,
        },
    }

    async def track_shipment(self, awb_code: str, carrier_name: str) -> Dict[str, Any]:
        tracking = self.MOCK_TRACKING.get(awb_code)
        if not tracking:
            raise ValueError(f"Tracking not found for AWB: {awb_code}")
        await asyncio.sleep(0.05)
        return dict(tracking)

class RealCarrierProvider:
    def __init__(self):
        from backend.app.core.config import settings
        self.api_key = settings.CARRIER_API_KEY
        if not self.api_key:
            raise NotImplementedError("RealCarrierProvider requires CARRIER_API_KEY credentials. Use CARRIER_PROVIDER=demo for local testing.")

    async def track_shipment(self, awb_code: str, carrier_name: str) -> Dict[str, Any]:
        # TODO: Implement real HTTPX logic for Delhivery/Bluedart here once credentials are provided
        raise NotImplementedError("Real carrier HTTP calls are not implemented in the skeleton yet.")

VALID_CARRIERS = {"delhivery", "bluedart", "ecom_express"}

@tool_handler
async def track_shipment(awb_code: str, carrier_name: str) -> Dict[str, Any]:
    if carrier_name.lower() not in VALID_CARRIERS:
        raise ValueError(f"Unsupported carrier: {carrier_name}. Must be one of {VALID_CARRIERS}")
    
    from backend.app.core.config import settings
    provider_type = settings.CARRIER_PROVIDER.lower()
    
    provider: CarrierProvider
    if provider_type == "demo":
        provider = DemoCarrierProvider()
    else:
        provider = RealCarrierProvider()
        
    return await provider.track_shipment(awb_code, carrier_name)
