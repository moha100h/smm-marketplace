"""Wallet handler — balance, deposit, transactions."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.user import User
from app.models.payment import Transaction, Payment, PaymentStatus, PaymentMethod
from app.bot.keyboards.inline import wallet_menu_kb, back_kb
from app.core.i18n import get_text
from app.core.config import settings

router = Router()


class DepositState(StatesGroup):
    amount = State()
    receipt = State()


def fmt(n: float) -> str:
    return f"{n:,.0f}"


@router.callback_query(F.data == "wallet:main")
async def wallet_main(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    """Show wallet balance."""
    level_emoji = {"bronze": "🥉", "silver": "🥈", "gold": "🥇", "diamond": "💎"}
    text = get_text(lang, "wallet_info",
        balance=fmt(user.wallet_balance),
        spent=fmt(user.total_spent),
        level=level_emoji.get(user.loyalty_level.value, "🥉") + " " + user.loyalty_level.value.upper(),
        orders=user.total_orders,
    )
    await cb.message.edit_text(text, reply_markup=wallet_menu_kb(lang).as_markup())
    await cb.answer()


@router.callback_query(F.data == "wallet:deposit")
async def deposit_start(cb: CallbackQuery, state: FSMContext, lang: str):
    """Start deposit process."""
    await cb.message.edit_text(get_text(lang, "deposit_amount"))
    await state.set_state(DepositState.amount)
    await cb.answer()


@router.message(DepositState.amount)
async def deposit_amount(msg: Message, state: FSMContext, lang: str):
    """Process deposit amount."""
    try:
        raw = msg.text.replace(",", "").replace(" ", "").replace(".", "")
        amount = int(raw)
        if amount < 10000:
            await msg.answer(get_text(lang, "deposit_min"))
            return
        await state.update_data(amount=amount)
        await msg.answer(get_text(lang, "deposit_receipt", amount=fmt(amount)))
        await state.set_state(DepositState.receipt)
    except (ValueError, AttributeError):
        await msg.answer(get_text(lang, "invalid_number"))


@router.message(DepositState.receipt)
async def deposit_receipt(msg: Message, state: FSMContext, session: AsyncSession, user: User, lang: str):
    """Process deposit receipt."""
    data = await state.get_data()
    amount = data.get("amount", 0)

    # Create payment record
    payment = Payment(
        user_id=user.tg_id,
        amount=amount,
        method=PaymentMethod.USDT_TRC20,
        status=PaymentStatus.SUBMITTED,
    )
    session.add(payment)
    await session.flush()

    # Notify admins
    caption = (
        f"💳 <b>درخواست واریز جدید</b>\n\n"
        f"👤 کاربر: {user.full_name or user.username} (<code>{user.tg_id}</code>)\n"
        f"💰 مبلغ: {fmt(amount)} تومان\n"
        f"🔢 شماره: #{payment.id}"
    )
    for admin_id in settings.admin_ids_list:
        try:
            if msg.photo:
                await msg.bot.send_photo(admin_id, msg.photo[-1].file_id, caption=caption,
                    reply_markup=None)  # Will add buttons below
                # Send inline buttons separately
                from aiogram.utils.keyboard import InlineKeyboardBuilder
                from aiogram.types import InlineKeyboardButton
                kb = InlineKeyboardBuilder()
                kb.row(
                    InlineKeyboardButton(text="✅ تأیید", callback_data=f"admin:dep:approve:{payment.id}"),
                    InlineKeyboardButton(text="❌ رد", callback_data=f"admin:dep:reject:{payment.id}"),
                )
                await msg.bot.send_message(admin_id, "اقدام:", reply_markup=kb.as_markup())
            else:
                from aiogram.utils.keyboard import InlineKeyboardBuilder
                from aiogram.types import InlineKeyboardButton
                kb = InlineKeyboardBuilder()
                kb.row(
                    InlineKeyboardButton(text="✅ تأیید", callback_data=f"admin:dep:approve:{payment.id}"),
                    InlineKeyboardButton(text="❌ رد", callback_data=f"admin:dep:reject:{payment.id}"),
                )
                await msg.bot.send_message(admin_id, caption + "\n\n📝 " + (msg.text or ""), reply_markup=kb.as_markup())
        except Exception:
            pass

    await msg.answer(get_text(lang, "deposit_sent"))
    await state.clear()


@router.callback_query(F.data == "wallet:tx")
async def wallet_transactions(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    """Show recent transactions."""
    r = await session.execute(
        select(Transaction)
        .where(Transaction.user_id == user.tg_id)
        .order_by(desc(Transaction.created_at))
        .limit(15)
    )
    txs = r.scalars().all()

    if not txs:
        text = get_text(lang, "no_transactions")
    else:
        lines = [f"📊 <b>{get_text(lang, 'transactions_btn')}</b>\n"]
        for tx in txs:
            sign = "+" if tx.amount > 0 else ""
            emoji = {"deposit": "💳", "purchase": "🛒", "refund": "↩️", "referral_bonus": "🎁"}.get(tx.type.value, "📋")
            lines.append(f"{emoji} {sign}{fmt(tx.amount)} | {tx.description or tx.type.value}")
        text = "\n".join(lines)

    await cb.message.edit_text(text, reply_markup=back_kb(lang).as_markup(), parse_mode="HTML")
    await cb.answer()
