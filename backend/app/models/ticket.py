"""Ticket and TicketMessage models."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship, foreign
from app.db.base import Base
import enum


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    subject = Column(String(256), nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", primaryjoin="foreign(Ticket.user_id) == User.tg_id", back_populates="tickets")
    messages = relationship("TicketMessage", back_populates="ticket", lazy="selectin")

    def __repr__(self):
        return f"<Ticket #{self.id} {self.subject}>"


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    sender_id = Column(BigInteger, nullable=False)
    is_admin = Column(Boolean, default=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="messages")

    def __repr__(self):
        return f"<TicketMessage #{self.id} ticket={self.ticket_id}>"
