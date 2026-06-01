"""SMM Provider & mapping models — multi-provider system."""
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class ProviderStatus(enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    UNHEALTHY = "unhealthy"


class MappingType(enum.Enum):
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    api_url = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    priority = Column(Integer, default=1)
    status = Column(SAEnum(ProviderStatus), default=ProviderStatus.ACTIVE)
    health_status = Column(String, default="ok")  # ok, slow, error
    response_time_ms = Column(Float, default=0.0)
    success_rate = Column(Float, default=100.0)
    error_rate = Column(Float, default=0.0)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    mappings = relationship("ServiceProviderMapping", back_populates="provider", cascade="all, delete-orphan")
    provider_orders = relationship("ProviderOrder", back_populates="provider")


class ServiceProviderMapping(Base):
    __tablename__ = "service_provider_mappings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    provider_service_id = Column(Integer, nullable=False)  # ID on provider side
    mapping_type = Column(SAEnum(MappingType), default=MappingType.ONE_TO_ONE)
    is_active = Column(Boolean, default=True)
    cost_override = Column(Integer, nullable=True)  # override provider cost

    service = relationship("Service", back_populates="provider_mappings")
    provider = relationship("Provider", back_populates="mappings")
