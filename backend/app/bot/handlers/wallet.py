"""Wallet handler — balance, deposit, transactions."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.user import User
from app.models.payment import Transaction
from app.bot.keyboards.menus import wallet_menu_kb, main_menu_kb, back_btn
from app.services.jalali import fmt_price

router = Router()


class DepositState(StatesGroup):
    amount = State()
    receipt = State()


@router.callback_query(F.data == "wallet:main")
async def wallet_main(cb: CallbackQuery, session: AsyncSession):
    """Show wallet balance."""
    user = await session.get(User, cb.from_user.id)
    if not user:
        await cb.answer("کاربر یافت نشد", show_alert=True)
        return

    text = (
        f"💰 کیف پول\n\n"
        f"موجودی: {fmt_price(user.wallet_balance)} تومان\n"
        f"کل خرید: {fmt_price(user.total_spent)} تومان\n"
        f"سطح وفاداری: {user.loyalty_level.value}"
    )
    await cb.message.edit_text(text, reply_markup=wallet_menu_kb().as_markup())
    await cb.answer()


@router.callback_query(F.data == "wallet:deposit")
async def deposit_start(cb: CallbackQuery, state: FSMContext):
    """Start deposit process."""
    await cb.message.edit_text(
        "💳 افزایش موجودی\n\nمبلغ مورد نظر را وارد کنید (تومان):",
        reply_markup=main_menu_kb().as_markup(),
    )
    await state.set_state(DepositState.amount)
    await cb.answer()


@router.message(DepositState.amount)
async def deposit_amount(msg: Message, state: FSMContext):
    """Process deposit amount input."""
    try:
        amount = int(msg.text.replace(",", "").replace(" ", ""))
        if amount < 10000:
            await msg.answer("⚠️ حداقل مبلغ ۱۰,۰۰۰ تومان است.")
            return
        await state.update_data(amount=amount)
        await msg.answer(
            f"📋 مبلغ: {fmt_price(amount)} تومان\n\n"
            f"لطفاً رسید پرداخت را ارسال کنید.",
        )
        await state.set_state(DepositState.receipt)
    except ValueError:
        await msg.answer("⚠️ لطفاً یک عدد معتبر وارد کنید.")


@router.message(DepositState.receipt)
async def deposit_receipt(msg: Message, state: FSMContext):
    """Process deposit receipt (photo or text)."""
    data = await state.get_data()
    amount = data.get("amount", 0)

    # Forward to admin
    from app.core.config import settings
    for admin_id in settings.admin_ids_list:
        try:
            if msg.photo:
                await msg.bot.send_photo(
                    admin_id,
                    msg.photo[-1].file_id,
                    caption=f"💳 درخواست واریز\n\nمبلغ: {fmt_price(amount)} تومان\nکاربر: {msg.from_user.full_name} ({msg.from_user.id})",
                )
            else:
                await msg.bot.send_message(
                    admin_id,
                    f"💳 درخواست واریز\n\nمبلغ: {fmt_price(amount)} تومان\nکاربر: {msg.from_user.full_name} ({msg.from_user.id})\n\nتوضیحات: {msg.text}",
                )
        except Exception:
            pass

    await msg.answer("✅ رسید شما ارسال شد. پس از بررسی، موجودی شما افزایش می‌یابد.")
    await state.clear()


@router.callback_query(F.data == "wallet:tx")
async def wallet_transactions(cb: CallbackQuery, session: AsyncSession):
    """Show recent transactions."""
    r = await session.execute(
        select(Transaction)
        .where(Transaction.user_id == cb.from_user.id)
        .order_by(desc(Transaction.created_at))
        .limit(10)
    )
    txs = r.scalars().all()

    if not txs:
        text = "📊 تراکنش‌ها\n\nهنوز تراکنشی ندارید."
    else:
        lines = ["📊 تراکنش‌های اخیر:\n"]
        for tx in txs:
            sign = "+" if tx.amount > 0 else ""
            lines.append(f"• {tx.type.value}: {sign}{tx.amount} | {tx.description or ''}")
        text = "\n".join(lines)

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    kb = InlineKeyboardBuilder()
    kb.row(back_btn)
    await cb.message.edit_text(text, reply_markup=kb.as_markup())
    await cb.answer()
