"""Ticket system models."""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class TicketPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    REOPENED = "reopened"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    subject = Column(String, nullable=False)
    category = Column(String, nullable=True)
    priority = Column(SAEnum(TicketPriority), default=TicketPriority.MEDIUM)
    status = Column(SAEnum(TicketStatus), default=TicketStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(BigInteger, nullable=False)  # sender
    message = Column(Text, nullable=False)
    attachment = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="messages")
