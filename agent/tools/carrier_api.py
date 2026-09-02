"""
DisputeSentinel AI — Carrier Tracking Integration

Provides shipment tracking via logistics provider APIs (Delhivery,
BlueDart, Ecom Express). Uses mock data in demo mode with realistic
Indian e-commerce delivery timelines.
"""

import asyncio
from typing import Dict, Any, List
from agent.tools.registry import tool_handler


# ── Mock Tracking Data ────────────────────────────────────
MOCK_TRACKING: Dict[str, Dict[str, Any]] = {
    "AWB123456789": {
        "carrier": "delhivery",
        "status": "DELIVERED",
        "events": [
            {"timestamp": "2024-01-16T10:00:00Z", "location": "Bangalore Hub", "description": "Shipment picked up from seller"},
            {"timestamp": "2024-01-16T22:30:00Z", "location": "Bangalore Sort Center", "description": "Package sorted and dispatched"},
            {"timestamp": "2024-01-17T08:30:00Z", "location": "Bangalore Delivery Center", "description": "Arrived at destination hub"},
            {"timestamp": "2024-01-17T10:15:00Z", "location": "Bangalore", "description": "Out for delivery"},
            {"timestamp": "2024-01-17T14:45:00Z", "location": "123 MG Road, Bangalore", "description": "Delivered - Signed by RAJESH"},
        ],
        "delivery_timestamp": "2024-01-17T14:45:00Z",
        "delivery_gps": {"lat": 12.9716, "lng": 77.5946},
        "pod_image_url": "https://storage.example.com/pod/AWB123456789.jpg",
    },
    "AWB987654321": {
        "carrier": "bluedart",
        "status": "IN_TRANSIT",
        "events": [
            {"timestamp": "2024-02-21T09:00:00Z", "location": "Kolkata Hub", "description": "Shipment picked up"},
            {"timestamp": "2024-02-22T14:00:00Z", "location": "Transit Hub", "description": "In transit to destination city"},
        ],
        "delivery_timestamp": None,
        "delivery_gps": None,
        "pod_image_url": None,
    },
    "AWB555666777": {
        "carrier": "ecom_express",
        "status": "DELIVERED",
        "events": [
            {"timestamp": "2024-03-06T08:00:00Z", "location": "Delhi Warehouse", "description": "Shipment picked up"},
            {"timestamp": "2024-03-06T20:00:00Z", "location": "Delhi Sort Center", "description": "Dispatched to destination"},
            {"timestamp": "2024-03-07T11:00:00Z", "location": "Connaught Place DC", "description": "Out for delivery"},
            {"timestamp": "2024-03-07T15:30:00Z", "location": "78 Connaught Place", "description": "Delivered - Signed by AMIT"},
        ],
        "delivery_timestamp": "2024-03-07T15:30:00Z",
        "delivery_gps": {"lat": 28.6315, "lng": 77.2167},
        "pod_image_url": "https://storage.example.com/pod/AWB555666777.jpg",
    },
    "AWB000111222": {
        "carrier": "delhivery",
        "status": "RTO",
        "events": [
            {"timestamp": "2024-04-11T09:00:00Z", "location": "Mumbai Hub", "description": "Shipment picked up"},
            {"timestamp": "2024-04-12T10:00:00Z", "location": "Mumbai DC", "description": "Out for delivery"},
            {"timestamp": "2024-04-12T18:00:00Z", "location": "Mumbai DC", "description": "Delivery attempt failed - Customer not available"},
            {"timestamp": "2024-04-13T10:00:00Z", "location": "Mumbai DC", "description": "Return to origin initiated"},
        ],
        "delivery_timestamp": None,
        "delivery_gps": None,
        "pod_image_url": None,
    },
}

VALID_CARRIERS = {"delhivery", "bluedart", "ecom_express"}


@tool_handler
async def track_shipment(awb_code: str, carrier_name: str) -> Dict[str, Any]:
    """Track a shipment via carrier logistics API.

    Args:
        awb_code: Air Waybill / tracking code.
        carrier_name: Carrier provider (delhivery, bluedart, ecom_express).

    Returns:
        Tracking data with status, events, delivery confirmation, and PoD URL.

    Raises:
        ValueError: If carrier is unsupported or AWB not found.
    """
    if carrier_name.lower() not in VALID_CARRIERS:
        raise ValueError(
            f"Unsupported carrier: {carrier_name}. Must be one of {VALID_CARRIERS}"
        )

    tracking = MOCK_TRACKING.get(awb_code)
    if not tracking:
        raise ValueError(f"Tracking not found for AWB: {awb_code}")

    # Simulate network latency
    await asyncio.sleep(0.05)

    return dict(tracking)  # Return a copy
