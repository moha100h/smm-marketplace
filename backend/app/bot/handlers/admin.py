"""Admin panel — order management, provider management, payments."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.order import Order, OrderStatus
from app.models.provider import Provider
from app.models.payment import Payment, PaymentStatus
from app.core.config import settings

router = Router()


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids_list


@router.message(F.text == "⚙️ پنل مدیریت")
async def admin_panel(msg: Message, session: AsyncSession):
    if not _is_admin(msg.from_user.id):
        return

    pending = (await session.execute(select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING))).scalar() or 0
    payments = (await session.execute(select(func.count(Payment.id)).where(Payment.status == PaymentStatus.SUBMITTED))).scalar() or 0

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=f"✅ نوبت‌های در انتظار ({pending})", callback_data="adm:pending"))
    kb.row(InlineKeyboardButton(text=f"💳 پرداخت‌های در انتظار ({payments})", callback_data="adm:payments"))
    kb.row(InlineKeyboardButton(text="📦 مدیریت پرووایدرها", callback_data="adm:providers"))
    kb.row(InlineKeyboardButton(text="📊 آمار", callback_data="adm:stats"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main"))

    await msg.answer("⚙️ <b>پنل مدیریت / Admin Panel</b>", reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "adm:pending")
async def adm_pending(cb: CallbackQuery, session: AsyncSession):
    r = await session.execute(
        select(Order).where(Order.status == OrderStatus.PENDING).order_by(Order.created_at.desc()).limit(20)
    )
    orders = r.scalars().all()

    if not orders:
        await cb.message.edit_text("✅ هیچ سفارش در انتظاری وجود ندارد")
        await cb.answer()
        return

    kb = InlineKeyboardBuilder()
    for o in orders:
        kb.row(InlineKeyboardButton(
            text=f"⏳ #{o.id} — {o.quantity:,} — {o.total_cost:,}",
            callback_data=f"adm:order:{o.id}"
        ))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm:main"))
    await cb.message.edit_text(f"⏳ {len(orders)} سفارش در انتظار:", reply_markup=kb.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("adm:order:"))
async def adm_order(cb: CallbackQuery, session: AsyncSession):
    order_id = int(cb.data.split(":")[2])
    order = await session.get(Order, order_id)
    if not order:
        await cb.answer("یافت نشد", show_alert=True)
        return

    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="✅ تایید", callback_data=f"adm:order:accept:{order_id}"),
        InlineKeyboardButton(text="❌ رد", callback_data=f"adm:order:reject:{order_id}"),
    )
    kb.row(InlineKeyboardButton(text="💈 انجام شد", callback_data=f"adm:order:done:{order_id}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm:pending"))

    text = (
        f"📋 <b>سفارش #{order.id}</b>
"
        f"━━━━━━━━━━━━━━━━━━
"
        f"🔢 تعداد: {order.quantity:,}
"
        f"💰 مبلغ: {order.total_cost:,}
"
        f"📊 وضعیت: {order.status.value}
"
        f"━━━━━━━━━━━━━━━━━━"
    )
    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()


@router.callback_query(F.data.startswith("adm:order:accept:"))
async def adm_order_accept(cb: CallbackQuery, session: AsyncSession):
    order_id = int(cb.data.split(":")[3])
    order = await session.get(Order, order_id)
    if order:
        order.status = OrderStatus.ACCEPTED
        await session.flush()
    await cb.answer("✅ تایید شد")
    await adm_order(cb, session)


@router.callback_query(F.data.startswith("adm:order:reject:"))
async def adm_order_reject(cb: CallbackQuery, session: AsyncSession):
    order_id = int(cb.data.split(":")[3])
    order = await session.get(Order, order_id)
    if order:
        order.status = OrderStatus.REJECTED
        # Refund
        user = await session.get(User, order.user_id)
        if user:
            user.wallet_balance += order.total_cost
        await session.flush()
    await cb.answer("❌ رد شد — مبلغ برگشت")
    await adm_order(cb, session)


@router.callback_query(F.data.startswith("adm:order:done:"))
async def adm_order_done(cb: CallbackQuery, session: AsyncSession):
    order_id = int(cb.data.split(":")[3])
    order = await session.get(Order, order_id)
    if order:
        order.status = OrderStatus.COMPLETED
        await session.flush()
    await cb.answer("💈 انجام شد")
    await adm_order(cb, session)
