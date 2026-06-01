from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Enum, ForeignKey, Float
from app.db.base import Base
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_1000 = Column(Integer, nullable=False)
    total_cost = Column(Integer, nullable=False)
    paid_amount = Column(Integer, default=0)
    charged_quantity = Column(Integer, default=0)
    refunded_amount = Column(Integer, default=0)
    form_data = Column(Text, nullable=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class ProviderOrder(Base):
    __tablename__ = "provider_orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    provider_order_ref = Column(String(128), nullable=True)
    provider_cost = Column(Float, nullable=True)
    status = Column(String(32), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
