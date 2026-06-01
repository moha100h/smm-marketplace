"""Wallet service — deposit, purchase, refund, referral bonus."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.payment import Transaction, TransactionType
from app.models.discount import Discount
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WalletService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_user(self, user_id: int):
        """Get user by tg_id."""
        r = await self.session.execute(select(User).where(User.tg_id == user_id))
        return r.scalar_one_or_none()

    async def process_deposit(self, user_id: int, amount: float, description: str = "Deposit") -> Transaction:
        """Add funds to user wallet."""
        user = await self._get_user(user_id)
        if not user:
            raise ValueError("User not found")

        balance_before = user.wallet_balance
        user.wallet_balance += amount

        tx = Transaction(
            user_id=user_id,
            type=TransactionType.DEPOSIT,
            amount=amount,
            balance_before=balance_before,
            balance_after=user.wallet_balance,
            description=description,
        )
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def process_purchase(
        self,
        user_id: int,
        amount: float,
        order_id: int,
        description: str = "Purchase",
    ) -> Transaction:
        """Deduct funds for a purchase."""
        user = await self._get_user(user_id)
        if not user:
            raise ValueError("User not found")
        if user.wallet_balance < amount:
            raise ValueError("Insufficient balance")

        balance_before = user.wallet_balance
        user.wallet_balance -= amount

        tx = Transaction(
            user_id=user_id,
            order_id=order_id,
            type=TransactionType.PURCHASE,
            amount=-amount,
            balance_before=balance_before,
            balance_after=user.wallet_balance,
            description=description,
        )
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def process_refund(
        self,
        user_id: int,
        amount: float,
        order_id: int,
        reason: str = "Refund",
    ) -> Transaction:
        """Refund funds to user wallet."""
        user = await self._get_user(user_id)
        if not user:
            raise ValueError("User not found")

        balance_before = user.wallet_balance
        user.wallet_balance += amount

        tx = Transaction(
            user_id=user_id,
            order_id=order_id,
            type=TransactionType.REFUND,
            amount=amount,
            balance_before=balance_before,
            balance_after=user.wallet_balance,
            description=reason,
        )
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def process_referral_bonus(self, user_id: int, bonus: float) -> Transaction:
        """Add referral bonus."""
        user = await self._get_user(user_id)
        if not user:
            raise ValueError("User not found")

        balance_before = user.wallet_balance
        user.wallet_balance += bonus

        tx = Transaction(
            user_id=user_id,
            type=TransactionType.REFERRAL_BONUS,
            amount=bonus,
            balance_before=balance_before,
            balance_after=user.wallet_balance,
            description="Referral bonus",
        )
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def apply_discount(self, code: str, amount: float) -> float:
        """Apply discount code and return final amount."""
        stmt = select(Discount).where(Discount.code == code, Discount.is_active == True)
        result = await self.session.execute(stmt)
        discount = result.scalar_one_or_none()

        if not discount:
            raise ValueError("Invalid discount code")
        if discount.max_uses and discount.used_count >= discount.max_uses:
            raise ValueError("Discount code expired")
        if discount.expires_at and discount.expires_at < datetime.utcnow():
            raise ValueError("Discount code expired")
        if amount < discount.min_order_amount:
            raise ValueError(f"Minimum order amount: {discount.min_order_amount}")

        discount.used_count += 1

        if discount.type.value == "percent":
            return amount * (1 - discount.value / 100)
        else:
            return max(0, amount - discount.value)
