"""Payment and Transaction models."""
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class PaymentMethod(str, enum.Enum):
    USDT_TRC20 = "usdt_trc20"
    USDT_BEP20 = "usdt_bep20"
    BTC = "btc"
    ETH = "eth"
    LTC = "ltc"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    tx_hash = Column(String(256), nullable=True)
    receipt_url = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")

    def __repr__(self):
        return f"<Payment #{self.id} {self.method.value} {self.amount}>"


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    PURCHASE = "purchase"
    REFUND = "refund"
    REFERRAL_BONUS = "referral_bonus"
    WITHDRAWAL = "withdrawal"
    ADJUSTMENT = "adjustment"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.tg_id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    balance_before = Column(Float, default=0)
    balance_after = Column(Float, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    order = relationship("Order", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction #{self.id} {self.type.value} {self.amount}>"
