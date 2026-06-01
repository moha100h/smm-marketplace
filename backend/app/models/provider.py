"""Provider and ServiceProviderMapping models."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class ProviderStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNHEALTHY = "unhealthy"


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    api_url = Column(String(512), nullable=False)
    api_key = Column(String(512), nullable=False)
    status = Column(Enum(ProviderStatus), default=ProviderStatus.ACTIVE)
    health_status = Column(String(32), default="ok")
    response_time_ms = Column(Float, default=0)
    success_rate = Column(Float, default=100.0)
    error_rate = Column(Float, default=0.0)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    provider_orders = relationship("ProviderOrder", back_populates="provider", foreign_keys="ProviderOrder.provider_id", lazy="selectin")
    service_mappings = relationship("ServiceProviderMapping", back_populates="provider", foreign_keys="ServiceProviderMapping.provider_id", lazy="selectin")

    def __repr__(self):
        return f"<Provider {self.name} status={self.status.value}>"


class ServiceProviderMapping(Base):
    __tablename__ = "service_provider_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    provider_service_id = Column(Integer, nullable=True)
    markup_percent = Column(Float, default=0)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    service = relationship("Service", foreign_keys=[service_id])
    provider = relationship("Provider", back_populates="service_mappings", foreign_keys=[provider_id])

    def __repr__(self):
        return f"<Mapping service={self.service_id} provider={self.provider_id}>"
