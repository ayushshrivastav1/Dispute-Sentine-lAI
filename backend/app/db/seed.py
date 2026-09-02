import asyncio
import logging
from datetime import datetime, timezone
from backend.app.db.session import async_session, engine
from backend.app.db.base import Base
from backend.app.models.order import Order
from backend.app.models.customer import Customer

# Import old mock data to seed
from agent.tools.db_client import MOCK_ORDERS, MOCK_CUSTOMERS

logger = logging.getLogger(__name__)

async def seed_database():
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Seeding database with demo records...")
    async with async_session() as db:
        # Seed Customers
        for email, data in MOCK_CUSTOMERS.items():
            customer = await db.get(Customer, email)
            if not customer:
                customer = Customer(
                    email=email,
                    total_orders=data.get("total_orders", 0),
                    successful_orders=data.get("successful_orders", 0),
                    previous_disputes=data.get("previous_disputes", 0),
                    account_tenure_days=data.get("account_tenure_days", 0),
                    ip_addresses_csv=",".join(data.get("ip_addresses", []))
                )
                db.add(customer)

        # Seed Orders
        for pay_id, data in MOCK_ORDERS.items():
            order = await db.get(Order, pay_id)
            if not order:
                created_dt = datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
                order = Order(
                    payment_id=pay_id,
                    order_id=data.get("order_id"),
                    amount=data.get("amount"),
                    currency=data.get("currency"),
                    customer_name=data.get("customer_name"),
                    customer_email=data.get("customer_email"),
                    shipping_address=data.get("shipping_address"),
                    billing_address=data.get("billing_address"),
                    carrier_name=data.get("carrier_name"),
                    awb_code=data.get("awb_code"),
                    ip_address=data.get("ip_address"),
                    device_fingerprint=data.get("device_fingerprint"),
                    created_at=created_dt
                )
                db.add(order)
        
        await db.commit()
    logger.info("Database seeding complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_database())
