"""User model — Telegram users, wallet, loyalty, referral."""
from sqlalchemy import Column, BigInteger, String, Boolean, Integer, DateTime, Enum as SAEnum, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class LoyaltyLevel(enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_tg_id", "tg_id", unique=True),
        Index("ix_users_referral_code", "referral_code", unique=True),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    language = Column(String, default="fa")  # fa | en
    is_blocked = Column(Boolean, default=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)

    # Wallet
    wallet_balance = Column(Integer, default=0)  # in smallest currency unit (e.g. toman cents)

    # Referral
    referral_code = Column(String, unique=True, nullable=True)
    referred_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Loyalty
    loyalty_level = Column(SAEnum(LoyaltyLevel), default=LoyaltyLevel.BRONZE)
    total_spent = Column(Integer, default=0)
    total_orders = Column(Integer, default=0)

    # Relations
    orders = relationship("Order", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    referrals = relationship("User", backref="referrer", remote_side=[id])

    @property
    def loyalty_discount(self) -> float:
        discounts = {
            LoyaltyLevel.BRONZE: 0,
            LoyaltyLevel.SILVER: 2,
            LoyaltyLevel.GOLD: 5,
            LoyaltyLevel.PLATINUM: 8,
            LoyaltyLevel.DIAMOND: 12,
        }
        return discounts.get(self.loyalty_level, 0)

    def update_loyalty(self):
        if self.total_spent >= 50_000_000:
            self.loyalty_level = LoyaltyLevel.DIAMOND
        elif self.total_spent >= 20_000_000:
            self.loyalty_level = LoyaltyLevel.PLATINUM
        elif self.total_spent >= 5_000_000:
            self.loyalty_level = LoyaltyLevel.GOLD
        elif self.total_spent >= 1_000_000:
            self.loyalty_level = LoyaltyLevel.SILVER
        else:
            self.loyalty_level = LoyaltyLevel.BRONZE
