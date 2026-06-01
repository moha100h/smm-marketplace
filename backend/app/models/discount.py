"""Discount & coupon models."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SAEnum
from datetime import datetime
import enum
from app.db.base import Base


class DiscountType(enum.Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class Discount(Base):
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True, nullable=False)
    discount_type = Column(SAEnum(DiscountType), default=DiscountType.PERCENTAGE)
    value = Column(Float, nullable=False)
    min_order_amount = Column(Integer, default=0)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
