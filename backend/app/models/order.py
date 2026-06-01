"""Order & ProviderOrder models — complete order lifecycle."""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class OrderStatus(enum.Enum):
    PENDING = "pending"
    AWAITING_REVIEW = "awaiting_review"
    ACCEPTED = "accepted"
    PROCESSING = "processing"
    PARTIALLY_COMPLETED = "partially_completed"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_service_id", "service_id"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    provider_order_id = Column(Integer, ForeignKey("provider_orders.id"), nullable=True)
    status = Column(SAEnum(OrderStatus), default=OrderStatus.PENDING)
    quantity = Column(Integer, nullable=False)
    charged_quantity = Column(Integer, nullable=True)  # actual delivered
    price_per_1000 = Column(Integer, nullable=False)
    total_cost = Column(Integer, nullable=False)
    paid_amount = Column(Integer, default=0)
    refunded_amount = Column(Integer, default=0)
    form_data = Column(Text, nullable=True)  # JSON string of form answers
    admin_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="orders")
    service = relationship("Service", back_populates="orders")
    provider_order = relationship("ProviderOrder", back_populates="order")
    transactions = relationship("Transaction", back_populates="order")


class ProviderOrder(Base):
    __tablename__ = "provider_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    provider_order_ref = Column(String, nullable=True)  # order ID on provider side
    status = Column(String, default="pending")
    quantity_ordered = Column(Integer, nullable=False)
    quantity_delivered = Column(Integer, default=0)
    cost = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    provider = relationship("Provider", back_populates="provider_orders")
    order = relationship("Order", back_populates="provider_order")
