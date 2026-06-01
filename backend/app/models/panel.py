"""Panel, Category, Service models — hierarchical marketplace structure."""
from sqlalchemy import Column, Integer, String, Boolean, Text, Float, DateTime, ForeignKey, Index, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class ServiceStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"


class PricingMode(enum.Enum):
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    DYNAMIC = "dynamic"


class Panel(Base):
    __tablename__ = "panels"
    __table_args__ = (Index("ix_panels_slug", "slug", unique=True),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    slug = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    categories = relationship("Category", back_populates="panel", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (Index("ix_categories_panel_id", "panel_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    panel_id = Column(Integer, ForeignKey("panels.id"), nullable=False)
    name = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    panel = relationship("Panel", back_populates="categories")
    subcategories = relationship("SubCategory", back_populates="category", cascade="all, delete-orphan")
    services = relationship("Service", back_populates="category")


class SubCategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    category = relationship("Category", back_populates="subcategories")
    services = relationship("Service", back_populates="subcategory")


class Service(Base):
    __tablename__ = "services"
    __table_args__ = (
        Index("ix_services_category_id", "category_id"),
        Index("ix_services_status", "status"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=True)
    name = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    price = Column(Integer, default=0)  # per 1000 units
    cost_price = Column(Integer, default=0)  # provider cost
    profit_margin = Column(Float, default=0.0)  # percentage
    pricing_mode = Column(SAEnum(PricingMode), default=PricingMode.FIXED)
    delivery_time = Column(String, nullable=True)  # e.g. "0-24 hours"
    min_quantity = Column(Integer, default=1)
    max_quantity = Column(Integer, default=100000)
    status = Column(SAEnum(ServiceStatus), default=ServiceStatus.ACTIVE)
    sort_order = Column(Integer, default=0)
    tags = Column(String, nullable=True)  # comma-separated
    refill_enabled = Column(Boolean, default=False)
    refill_days = Column(Integer, default=30)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="services")
    subcategory = relationship("SubCategory", back_populates="services")
    provider_mappings = relationship("ServiceProviderMapping", back_populates="service", cascade="all, delete-orphan")
    order_forms = relationship("OrderForm", back_populates="service", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="service")
