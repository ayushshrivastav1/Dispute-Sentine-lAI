from sqlalchemy import Column, String, Integer
from backend.app.db.base import Base

class Customer(Base):
    __tablename__ = "customers"

    email = Column(String, primary_key=True, index=True)
    total_orders = Column(Integer, default=0)
    successful_orders = Column(Integer, default=0)
    previous_disputes = Column(Integer, default=0)
    account_tenure_days = Column(Integer, default=0)
    ip_addresses_csv = Column(String) # Simple CSV store for IPs
