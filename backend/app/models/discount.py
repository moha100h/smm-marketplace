from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Enum
from app.db.base import Base
import enum


class DiscountType(str, enum.Enum):
    PERCENT = "percent"
    FIXED = "fixed"


class Discount(Base):
    __tablename__ = "discounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(64), unique=True, nullable=False)
    type = Column(Enum(DiscountType), nullable=False)
    value = Column(Float, nullable=False)
    min_order_amount = Column(Float, default=0)
    max_uses = Column(Integer, nullable=True)
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
