"""Order and ProviderOrder models."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    AWAITING_REVIEW = "awaiting_review"
    ACCEPTED = "accepted"
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

    user = relationship("User", back_populates="orders",
        primaryjoin="Order.user_id == foreign(User.tg_id)")
    service = relationship("Service", back_populates="orders", foreign_keys=[service_id])
    provider_orders = relationship("ProviderOrder", back_populates="order", foreign_keys="ProviderOrder.order_id", lazy="selectin")
    transactions = relationship("Transaction", back_populates="order", foreign_keys="Transaction.order_id", lazy="selectin")

    def __repr__(self):
        return f"<Order #{self.id} status={self.status.value}>"


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

    order = relationship("Order", back_populates="provider_orders", foreign_keys=[order_id])
    provider = relationship("Provider", back_populates="provider_orders", foreign_keys=[provider_id])

    def __repr__(self):
        return f"<ProviderOrder #{self.id} ref={self.provider_order_ref}>"
