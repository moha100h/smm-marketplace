"""Orders handler — new order, my orders, order status."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.panel import Service
from app.bot.keyboards.menus import main_menu_kb, back_btn
from app.services.jalali import fmt_price
from app.services.order_service import OrderService

router = Router()


class OrderState(StatesGroup):
    service = State()
    quantity = State()
    form_data = State()


@router.callback_query(F.data == "ord:new")
async def new_order_start(cb: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Start new order flow."""
    r = await session.execute(
        select(Service).where(Service.status == "active").order_by(Service.name).limit(20)
    )
    services = r.scalars().all()

    if not services:
        await cb.message.edit_text("⚠️ هیچ خدمتی فعال نیست.", reply_markup=main_menu_kb().as_markup())
        await cb.answer()
        return

    kb = InlineKeyboardBuilder()
    for s in services:
        kb.row(InlineKeyboardButton(text=f"{s.name} — {fmt_price(s.price)}", callback_data=f"ord:svc:{s.id}"))
    kb.row(back_btn)

    await cb.message.edit_text("🛒 انتخاب خدمت:", reply_markup=kb.as_markup())
    await state.set_state(OrderState.service)
    await cb.answer()


@router.callback_query(F.data.startswith("ord:svc:"))
async def order_select_service(cb: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Select service for order."""
    service_id = int(cb.data.split(":")[2])
    await state.update_data(service_id=service_id)

    service = await session.get(Service, service_id)
    if not service:
        await cb.answer("خدمت یافت نشد", show_alert=True)
        return

    await cb.message.edit_text(
        f"📦 {service.name}\n\n"
        f"قیمت: {fmt_price(service.price)} per 1000\n"
        f"حداقل: {service.min_quantity}\n"
        f"حداکثر: {service.max_quantity}\n\n"
        f"تعداد را وارد کنید:",
    )
    await state.set_state(OrderState.quantity)
    await cb.answer()


@router.message(OrderState.quantity)
async def order_quantity(msg: Message, session: AsyncSession, state: FSMContext):
    """Process quantity input."""
    try:
        quantity = int(msg.text.replace(",", "").replace(" ", ""))
        data = await state.get_data()
        service_id = data.get("service_id")
        service = await session.get(Service, service_id)

        if not service:
            await msg.answer("⚠️ خدمت یافت نشد.")
            await state.clear()
            return

        if quantity < service.min_quantity or quantity > service.max_quantity:
            await msg.answer(f"⚠️ تعداد باید بین {service.min_quantity} و {service.max_quantity} باشد.")
            return

        total_cost = (quantity * service.price) // 1000
        await state.update_data(quantity=quantity, total_cost=total_cost)

        # Check balance
        user = await session.get(User, msg.from_user.id)
        if user.wallet_balance < total_cost:
            await msg.answer(
                f"⚠️ موجودی کافی نیست.\n\n"
                f"هزینه: {fmt_price(total_cost)} تومان\n"
                f"موجودی: {fmt_price(user.wallet_balance)} تومان"
            )
            await state.clear()
            return

        await msg.answer(
            f"📋 خلاصه سفارش:\n\n"
            f"خدمت: {service.name}\n"
            f"تعداد: {quantity}\n"
            f"هزینه: {fmt_price(total_cost)} تومان\n\n"
            f"لینک/اطلاعات مورد نیاز را ارسال کنید:",
        )
        await state.set_state(OrderState.form_data)
    except ValueError:
        await msg.answer("⚠️ لطفاً یک عدد معتبر وارد کنید.")


@router.message(OrderState.form_data)
async def order_submit(msg: Message, session: AsyncSession, state: FSMContext):
    """Submit order."""
    data = await state.get_data()
    service_id = data.get("service_id")
    quantity = data.get("quantity")
    total_cost = data.get("total_cost")
    form_data = msg.text

    if not all([service_id, quantity, total_cost]):
        await msg.answer("⚠️ خطا در پردازش سفارش. دوباره شروع کنید.")
        await state.clear()
        return

    try:
        order_service = OrderService(session)
        order = await order_service.create_order(
            user_id=msg.from_user.id,
            service_id=service_id,
            quantity=quantity,
            price_per_1000=total_cost * 1000 // quantity if quantity else 0,
            form_data=form_data,
        )

        await msg.answer(
            f"✅ سفارش ثبت شد!\n\n"
            f"شماره سفارش: #{order.id}\n"
            f"وضعیت: {order.status.value}\n"
            f"هزینه: {fmt_price(total_cost)} تومان",
            reply_markup=main_menu_kb().as_markup(),
        )
    except ValueError as e:
        await msg.answer(f"❌ خطا: {str(e)}", reply_markup=main_menu_kb().as_markup())

    await state.clear()


@router.callback_query(F.data == "ord:my")
async def my_orders(cb: CallbackQuery, session: AsyncSession):
    """Show user's orders."""
    r = await session.execute(
        select(Order)
        .where(Order.user_id == cb.from_user.id)
        .order_by(desc(Order.created_at))
        .limit(10)
    )
    orders = r.scalars().all()

    if not orders:
        text = "📋 سفارشات من\n\nهنوز سفارشی ندارید."
    else:
        lines = ["📋 سفارشات اخیر:\n"]
        for o in orders:
            status_emoji = {"pending": "⏳", "completed": "✅", "cancelled": "❌", "processing": "🔄"}.get(o.status.value, "📦")
            lines.append(f"{status_emoji} #{o.id} — {o.status.value} — {fmt_price(o.total_cost)}")
        text = "\n".join(lines)

    kb = InlineKeyboardBuilder()
    kb.row(back_btn)
    await cb.message.edit_text(text, reply_markup=kb.as_markup())
    await cb.answer()


@router.callback_query(F.data == "ord:panels")
async def order_panels(cb: CallbackQuery, session: AsyncSession):
    """Show available panels for ordering."""
    from app.models.panel import Panel
    r = await session.execute(select(Panel).where(Panel.is_active == True))
    panels = r.scalars().all()

    if not panels:
        await cb.message.edit_text("⚠️ هیچ پنلی فعال نیست.", reply_markup=main_menu_kb().as_markup())
        await cb.answer()
        return

    kb = InlineKeyboardBuilder()
    for p in panels:
        kb.row(InlineKeyboardButton(text=f"📂 {p.name}", callback_data=f"ord:panel:{p.id}"))
    kb.row(back_btn)

    await cb.message.edit_text("📦 انتخاب پنل:", reply_markup=kb.as_markup())
    await cb.answer()
