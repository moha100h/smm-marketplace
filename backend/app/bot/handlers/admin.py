"""Admin handler — approve deposits, manage orders, stats."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus, Transaction
from app.bot.keyboards.menus import main_menu_kb, back_btn
from app.core.config import settings
from app.services.jalali import fmt_price

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids_list


@router.message(F.text == "📊 آمار")
async def admin_stats(msg: Message, session: AsyncSession):
    """Show admin statistics."""
    if not is_admin(msg.from_user.id):
        return

    total_users = await session.scalar(select(func.count(User.id)))
    total_orders = await session.scalar(select(func.count(Order.id)))
    total_revenue = await session.scalar(select(func.sum(Order.total_cost)) or 0)

    text = (
        f"📊 آمار کلی\n\n"
        f"👥 کاربران: {total_users}\n"
        f"📦 سفارشات: {total_orders}\n"
        f"💰 درآمد کل: {fmt_price(total_revenue)} تومان"
    )
    await msg.answer(text)


@router.callback_query(F.data.startswith("admin:deposit:"))
async def admin_deposit_action(cb: CallbackQuery, session: AsyncSession):
    """Approve or reject deposit."""
    parts = cb.data.split(":")
    action = parts[2]  # approve or reject
    payment_id = int(parts[3])

    payment = await session.get(Payment, payment_id)
    if not payment:
        await cb.answer("پرداخت یافت نشد", show_alert=True)
        return

    r = await session.execute(select(User).where(User.tg_id == payment.user_id))
    user = r.scalar_one_or_none()
    if not user:
        await cb.answer("کاربر یافت نشد", show_alert=True)
        return

    if action == "approve":
        payment.status = PaymentStatus.CONFIRMED
        user.wallet_balance += payment.amount

        tx = Transaction(
            user_id=user.tg_id,
            type=TransactionType.DEPOSIT,
            amount=payment.amount,
            balance_before=user.wallet_balance - payment.amount,
            balance_after=user.wallet_balance,
            description="Deposit approved",
        )
        session.add(tx)
        await session.flush()

        try:
            await cb.bot.send_message(
                user.tg_id,
                f"✅ واریز شما تأیید شد.\n\nمبلغ: {fmt_price(payment.amount)} تومان\nموجودی جدید: {fmt_price(user.wallet_balance)} تومان",
            )
        except Exception:
            pass

        await cb.message.edit_text(f"✅ واریز #{payment_id} تأیید شد.")
    elif action == "reject":
        payment.status = PaymentStatus.REJECTED
        await session.flush()

        try:
            await cb.bot.send_message(
                user.tg_id,
                f"❌ واریز شما رد شد.\n\nمبلغ: {fmt_price(payment.amount)} تومان\nلطفاً با پشتیبانی تماس بگیرید.",
            )
        except Exception:
            pass

        await cb.message.edit_text(f"❌ واریز #{payment_id} رد شد.")

    await cb.answer()


@router.callback_query(F.data.startswith("admin:order:"))
async def admin_order_action(cb: CallbackQuery, session: AsyncSession):
    """Update order status."""
    parts = cb.data.split(":")
    status = parts[2]
    order_id = int(parts[3])

    order = await session.get(Order, order_id)
    if not order:
        await cb.answer("سفارش یافت نشد", show_alert=True)
        return

    order.status = OrderStatus(status)
    await session.flush()

    r = await session.execute(select(User).where(User.tg_id == order.user_id))
    user = r.scalar_one_or_none()
    if user:
        try:
            await cb.bot.send_message(
                user.tg_id,
                f"📦 وضعیت سفارش #{order.id} تغییر کرد به: {order.status.value}",
            )
        except Exception:
            pass

    await cb.message.edit_text(f"✅ سفارش #{order_id} -> {status}")
    await cb.answer()
