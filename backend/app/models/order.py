from sqlalchemy import Column, String, Integer, DateTime
from backend.app.db.base import Base

class Order(Base):
    __tablename__ = "orders"

    payment_id = Column(String, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String, default="INR")
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False, index=True)
    shipping_address = Column(String)
    billing_address = Column(String)
    carrier_name = Column(String)
    awb_code = Column(String)
    ip_address = Column(String)
    device_fingerprint = Column(String)
    created_at = Column(DateTime)
