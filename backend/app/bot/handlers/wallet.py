"""Wallet handler — balance, deposit, transactions."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.payment import Transaction
from app.services.jalali import fmt_price
from app.core.config import settings

router = Router()


@router.message(F.text.in_(["💰 کیف پول", "💰 Wallet"]))
async def show_wallet(msg: Message, session: AsyncSession):
    user = await session.get(User, msg.from_user.id)
    if not user:
        await msg.answer("⚠️ ابتدا ثبت‌نام کنید / Please register first")
        return

    text = (
        f"💰 <b>کیف پول / Wallet</b>
"
        f"━━━━━━━━━━━━━━━━━━
"
        f"💎 موجودی: <b>{fmt_price(user.wallet_balance)}</b>
"
        f"🏆 سطح: <b>{user.loyalty_level.value}</b>
"
        f"📊 کل سفارشات: <b>{user.total_orders}</b>
"
        f"💸 کل هزینه: <b>{fmt_price(user.total_spent)}</b>
"
        f"━━━━━━━━━━━━━━━━━━"
    )

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="💳 شارژ کیف پول / Deposit", callback_data="wallet:deposit"))
    kb.row(InlineKeyboardButton(text="📋 تراکنش‌ها / Transactions", callback_data="wallet:tx"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت / Back", callback_data="nav:main"))

    await msg.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "wallet:deposit")
async def wallet_deposit(cb: CallbackQuery):
    text = (
        f"💳 <b>شارژ کیف پول / Deposit</b>

"
        f"مبلغ را به یکی از آدرس‌های زیر واریز کنید:

"
        f"🔵 <b>USDT TRC20:</b>
<code>{settings.USDT_TRC20_ADDRESS or 'تنظیم نشده'}</code>

"
        f"🟡 <b>USDT BEP20:</b>
<code>{settings.USDT_BEP20_ADDRESS or 'تنظیم نشده'}</code>

"
        f"پس از واریز، تصویر رسید را ارسال کنید."
    )
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📸 ارسال رسید", callback_data="wallet:send_receipt"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main"))
    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data == "wallet:tx")
async def wallet_transactions(cb: CallbackQuery, session: AsyncSession):
    stmt = (
        select(Transaction)
        .where(Transaction.user_id == cb.from_user.id)
        .order_by(Transaction.created_at.desc())
        .limit(10)
    )
    result = await session.execute(stmt)
    txs = result.scalars().all()

    if not txs:
        await cb.message.edit_text("📋 تراکنشی یافت نشد / No transactions", reply_markup=InlineKeyboardBuilder().row(
            InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main")
        ).as_markup())
        await cb.answer()
        return

    lines = ["📋 <b>آخرین تراکنش‌ها:</b>
"]
    for tx in txs:
        icon = "➕" if tx.amount > 0 else "➖"
        lines.append(f"{icon} {tx.description or tx.type.value}: <b>{fmt_price(abs(tx.amount))}</b>")

    text = "
".join(lines)
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main"))
    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()
