from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Boolean
from app.db.base import Base
import enum


class FieldType(str, enum.Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    URL = "url"
    SELECT = "select"


class OrderForm(Base):
    __tablename__ = "order_forms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    field_type = Column(Enum(FieldType), nullable=False)
    field_label = Column(String(256), nullable=False)
    field_label_en = Column(String(256), nullable=True)
    field_placeholder = Column(String(256), nullable=True)
    is_required = Column(Boolean, default=True)
    options = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
