"""User model — authentication, wallet, loyalty, referral."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Enum, Float, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class LoyaltyLevel(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    DIAMOND = "diamond"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(128), nullable=True)
    full_name = Column(String(256), nullable=True)
    language = Column(String(8), default="fa")
    wallet_balance = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    loyalty_level = Column(Enum(LoyaltyLevel), default=LoyaltyLevel.BRONZE)
    referral_code = Column(String(32), unique=True, nullable=True)
    referred_by_id = Column(Integer, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_banned = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    # Relationships — lazy="selectin" to avoid lazy-load errors in async
    orders = relationship("Order", back_populates="user", foreign_keys="Order.user_id", lazy="selectin")
    transactions = relationship("Transaction", back_populates="user", foreign_keys="Transaction.user_id", lazy="selectin")
    tickets = relationship("Ticket", back_populates="user", foreign_keys="Ticket.user_id", lazy="selectin")
    notifications = relationship("Notification", back_populates="user", foreign_keys="Notification.user_id", lazy="selectin")

    def update_loyalty(self):
        """Auto-update loyalty level based on total_spent."""
        if self.total_spent >= 10000:
            self.loyalty_level = LoyaltyLevel.DIAMOND
        elif self.total_spent >= 5000:
            self.loyalty_level = LoyaltyLevel.GOLD
        elif self.total_spent >= 1000:
            self.loyalty_level = LoyaltyLevel.SILVER
        else:
            self.loyalty_level = LoyaltyLevel.BRONZE

    def __repr__(self):
        return f"<User tg_id={self.tg_id} level={self.loyalty_level.value}>"
