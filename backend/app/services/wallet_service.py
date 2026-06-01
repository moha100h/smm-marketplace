"""Wallet service — transactions, deposits, refunds."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.payment import Transaction, TransactionType
from app.repositories.user_repo import UserRepository
from datetime import datetime


class WalletService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def process_deposit(self, user_id: int, amount: int, description: str = "Deposit") -> Transaction:
        """Add funds to user wallet and record transaction."""
        user = await self.user_repo.session.get(User, user_id)
        balance_before = user.wallet_balance

        user.wallet_balance += amount
        await self.session.flush()

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

    async def process_purchase(self, user_id: int, amount: int, order_id: int) -> Transaction:
        """Deduct funds for purchase."""
        user = await self.user_repo.session.get(User, user_id)
        if user.wallet_balance < amount:
            raise ValueError("Insufficient wallet balance")

        balance_before = user.wallet_balance
        user.wallet_balance -= amount
        await self.session.flush()

        tx = Transaction(
            user_id=user_id,
            order_id=order_id,
            type=TransactionType.PURCHASE,
            amount=-amount,
            balance_before=balance_before,
            balance_after=user.wallet_balance,
            description=f"Order #{order_id} purchase",
        )
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def process_refund(self, user_id: int, amount: int, order_id: int, reason: str = "Refund") -> Transaction:
        """Refund funds to user wallet."""
        user = await self.user_repo.session.get(User, user_id)
        balance_before = user.wallet_balance

        user.wallet_balance += amount
        await self.session.flush()

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

    async def process_referral_bonus(self, user_id: int, amount: int) -> Transaction:
        """Add referral commission."""
        user = await self.user_repo.session.get(User, user_id)
        balance_before = user.wallet_balance

        user.wallet_balance += amount
        await self.session.flush()

        tx = Transaction(
            user_id=user_id,
            type=TransactionType.REFERRAL_BONUS,
            amount=amount,
            balance_before=balance_before,
            balance_after=user.wallet_balance,
            description="Referral commission",
        )
        self.session.add(tx)
        await self.session.flush()
        return tx
