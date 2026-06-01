"""Payment & Transaction models — wallet, crypto, refunds."""
from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Enum as SAEnum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base


class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PURCHASE = "purchase"
    REFUND = "refund"
    REFERRAL_BONUS = "referral_bonus"
    MANUAL_ADJUSTMENT = "manual_adjustment"
    CANCELLATION_REFUND = "cancellation_refund"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class PaymentMethod(enum.Enum):
    USDT_TRC20 = "usdt_trc20"
    USDT_BEP20 = "usdt_bep20"
    BTC = "btc"
    ETH = "eth"
    LTC = "ltc"


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (Index("ix_payments_user_id", "user_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    method = Column(SAEnum(PaymentMethod), nullable=False)
    amount = Column(Integer, nullable=False)  # requested amount
    amount_usd = Column(Integer, nullable=True)  # USD equivalent in cents
    status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    tx_hash = Column(String, nullable=True)
    receipt_file = Column(String, nullable=True)
    wallet_address = Column(String, nullable=True)  # deposit address shown to user
    admin_note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="payments")


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_user_id", "user_id"),
        Index("ix_transactions_type", "type"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    type = Column(SAEnum(TransactionType), nullable=False)
    amount = Column(Integer, nullable=False)  # positive=credit, negative=debit
    balance_before = Column(Integer, default=0)
    balance_after = Column(Integer, default=0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    order = relationship("Order", back_populates="transactions")
