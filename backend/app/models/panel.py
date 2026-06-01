"""Panel, Category, SubCategory, Service models — marketplace hierarchy."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Panel(Base):
    __tablename__ = "panels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    categories = relationship("Category", back_populates="panel", foreign_keys="Category.panel_id", lazy="selectin")

    def __repr__(self):
        return f"<Panel {self.name}>"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    panel_id = Column(Integer, ForeignKey("panels.id"), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    panel = relationship("Panel", back_populates="categories", foreign_keys=[panel_id])
    subcategories = relationship("SubCategory", back_populates="category", foreign_keys="SubCategory.category_id", lazy="selectin")
    services = relationship("Service", back_populates="category", foreign_keys="Service.category_id", lazy="selectin")

    def __repr__(self):
        return f"<Category {self.name}>"


class SubCategory(Base):
    __tablename__ = "subcategories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="subcategories", foreign_keys=[category_id])
    services = relationship("Service", back_populates="subcategory", foreign_keys="Service.subcategory_id", lazy="selectin")

    def __repr__(self):
        return f"<SubCategory {self.name}>"


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=True)
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    min_quantity = Column(Integer, default=1)
    max_quantity = Column(Integer, default=100000)
    status = Column(String(32), default="active")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="services", foreign_keys=[category_id])
    subcategory = relationship("SubCategory", back_populates="services", foreign_keys=[subcategory_id])
    orders = relationship("Order", back_populates="service", foreign_keys="Order.service_id", lazy="selectin")
    form_fields = relationship("OrderForm", back_populates="service", foreign_keys="OrderForm.service_id", lazy="selectin")

    def __repr__(self):
        return f"<Service {self.name} price={self.price}>"
