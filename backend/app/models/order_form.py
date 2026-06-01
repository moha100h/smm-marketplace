"""Dynamic order form models — custom fields per service."""
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class FieldType(enum.Enum):
    TEXT = "text"
    NUMBER = "number"
    URL = "url"
    SELECT = "select"
    CHECKBOX = "checkbox"
    FILE = "file"
    MULTI_SELECT = "multi_select"
    TEXTAREA = "textarea"


class OrderForm(Base):
    __tablename__ = "order_forms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    field_name = Column(String, nullable=False)
    field_label = Column(String, nullable=False)
    field_label_en = Column(String, nullable=True)
    field_type = Column(SAEnum(FieldType), default=FieldType.TEXT)
    is_required = Column(Boolean, default=True)
    options = Column(Text, nullable=True)  # JSON array for select/multi_select
    placeholder = Column(String, nullable=True)
    placeholder_en = Column(String, nullable=True)
    sort_order = Column(Integer, default=0)

    service = relationship("Service", back_populates="order_forms")
