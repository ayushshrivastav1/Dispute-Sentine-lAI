"""
DisputeSentinel AI — Simulated Read-Only Database Client

Provides mock order lookups and customer history queries for
development and demo purposes. In production, these would query
actual PostgreSQL tables via SQLAlchemy.
"""

from typing import Dict, Any
from agent.tools.registry import tool_handler

# ── Mock Order Data ───────────────────────────────────────
# Amounts in paise (INR × 100). Includes carrier/AWB info.
MOCK_ORDERS: Dict[str, Dict[str, Any]] = {
    "pay_EFtmUsbwpXwBHI": {
        "order_id": "order_EKwxw5LRhOMZ",
        "amount": 500000,           # ₹5,000
        "currency": "INR",
        "customer_name": "Rajesh Kumar",
        "customer_email": "rajesh.kumar@example.com",
        "shipping_address": "123, MG Road, Bangalore, Karnataka 560001",
        "billing_address": "123, MG Road, Bangalore, Karnataka 560001",
        "carrier_name": "delhivery",
        "awb_code": "AWB123456789",
        "ip_address": "192.168.1.100",
        "device_fingerprint": "fp_a1b2c3d4e5f6",
        "created_at": "2024-01-15T10:30:00Z",
    },
    "pay_HZbvHkJmKlNoPq": {
        "order_id": "order_HZcvTkRmPqStUv",
        "amount": 1500000,          # ₹15,000
        "currency": "INR",
        "customer_name": "Priya Sharma",
        "customer_email": "priya.s@example.com",
        "shipping_address": "45, Park Street, Kolkata, West Bengal 700016",
        "billing_address": "789, Salt Lake, Kolkata, West Bengal 700091",
        "carrier_name": "bluedart",
        "awb_code": "AWB987654321",
        "ip_address": "172.16.0.50",
        "device_fingerprint": "fp_x9y8z7w6v5u4",
        "created_at": "2024-02-20T14:45:00Z",
    },
    "pay_QRsTuVwXyZaBcD": {
        "order_id": "order_QRdEfGhIjKlMnO",
        "amount": 3500000,          # ₹35,000 (above auto-contest threshold)
        "currency": "INR",
        "customer_name": "Amit Singh",
        "customer_email": "amit.singh@example.com",
        "shipping_address": "78, Connaught Place, New Delhi, Delhi 110001",
        "billing_address": "78, Connaught Place, New Delhi, Delhi 110001",
        "carrier_name": "ecom_express",
        "awb_code": "AWB555666777",
        "ip_address": "192.168.10.15",
        "device_fingerprint": "fp_m3n4o5p6q7r8",
        "created_at": "2024-03-05T09:15:00Z",
    },
    "pay_UndeliveredCase": {
        "order_id": "order_UndeliveredTest",
        "amount": 200000,           # ₹2,000
        "currency": "INR",
        "customer_name": "Vikram Patel",
        "customer_email": "vikram.p@example.com",
        "shipping_address": "12, Marine Drive, Mumbai, Maharashtra 400001",
        "billing_address": "12, Marine Drive, Mumbai, Maharashtra 400001",
        "carrier_name": "delhivery",
        "awb_code": "AWB000111222",
        "ip_address": "10.0.0.99",
        "device_fingerprint": "fp_t1u2v3w4x5y6",
        "created_at": "2024-04-10T16:00:00Z",
    },
}

# ── Mock Customer History ─────────────────────────────────
MOCK_CUSTOMERS: Dict[str, Dict[str, Any]] = {
    "rajesh.kumar@example.com": {
        "total_orders": 15,
        "successful_orders": 14,
        "previous_disputes": 0,
        "account_tenure_days": 450,
        "ip_addresses": ["192.168.1.100", "10.0.0.5"],
    },
    "priya.s@example.com": {
        "total_orders": 3,
        "successful_orders": 1,
        "previous_disputes": 2,
        "account_tenure_days": 30,
        "ip_addresses": ["172.16.0.50"],
    },
    "amit.singh@example.com": {
        "total_orders": 50,
        "successful_orders": 50,
        "previous_disputes": 0,
        "account_tenure_days": 1200,
        "ip_addresses": ["192.168.10.15", "192.168.10.20"],
    },
    "vikram.p@example.com": {
        "total_orders": 2,
        "successful_orders": 1,
        "previous_disputes": 1,
        "account_tenure_days": 15,
        "ip_addresses": ["10.0.0.99"],
    },
}


from typing import Dict, Any
from sqlalchemy import select
from backend.app.db.session import async_session
from backend.app.models.order import Order
from backend.app.models.customer import Customer
from agent.tools.registry import tool_handler

@tool_handler
async def fetch_order_details(payment_id: str) -> Dict[str, Any]:
    """Fetch order details by payment ID.

    Args:
        payment_id: Razorpay payment identifier (pay_...).

    Returns:
        Order details including shipping info and carrier/AWB data.

    Raises:
        ValueError: If payment_id is not found in the database.
    """
    async with async_session() as db:
        stmt = select(Order).where(Order.payment_id == payment_id)
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order not found for payment_id: {payment_id}")
            
        return {
            "order_id": order.order_id,
            "amount": order.amount,
            "currency": order.currency,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "shipping_address": order.shipping_address,
            "billing_address": order.billing_address,
            "carrier_name": order.carrier_name,
            "awb_code": order.awb_code,
            "ip_address": order.ip_address,
            "device_fingerprint": order.device_fingerprint,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }

@tool_handler
async def fetch_customer_history(customer_email: str) -> Dict[str, Any]:
    """Fetch customer purchase and dispute history by email.

    Args:
        customer_email: Customer's email address.

    Returns:
        Customer history including order counts, dispute counts, and known IPs.
    """
    async with async_session() as db:
        stmt = select(Customer).where(Customer.email == customer_email)
        result = await db.execute(stmt)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return {
                "total_orders": 0,
                "successful_orders": 0,
                "previous_disputes": 0,
                "account_tenure_days": 0,
                "ip_addresses": [],
            }
            
        ips = customer.ip_addresses_csv.split(",") if customer.ip_addresses_csv else []
        return {
            "total_orders": customer.total_orders,
            "successful_orders": customer.successful_orders,
            "previous_disputes": customer.previous_disputes,
            "account_tenure_days": customer.account_tenure_days,
            "ip_addresses": [ip for ip in ips if ip],
        }
