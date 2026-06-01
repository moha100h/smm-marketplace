"""Orders handler — browse panels, categories, services, place orders."""
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
from app.models.panel import Panel, Category, SubCategory, Service
from app.models.payment import Transaction, TransactionType
from app.bot.keyboards.inline import back_kb, main_menu_kb
from app.core.i18n import get_text

router = Router()


class OrderState(StatesGroup):
    service = State()
    quantity = State()
    form_data = State()


def fmt(n: float) -> str:
    return f"{n:,.0f}"


def name_of(obj, lang: str) -> str:
    """Get localized name."""
    if lang == "en" and getattr(obj, "name_en", None):
        return obj.name_en
    return obj.name


@router.callback_query(F.data == "ord:new")
async def new_order_start(cb: CallbackQuery, session: AsyncSession, lang: str):
    """Show available panels."""
    r = await session.execute(select(Panel).where(Panel.is_active == True).order_by(Panel.sort_order))
    panels = r.scalars().all()

    if not panels:
        await cb.message.edit_text(get_text(lang, "no_panels"), reply_markup=back_kb(lang).as_markup())
        await cb.answer()
        return

    kb = InlineKeyboardBuilder()
    for p in panels:
        kb.row(InlineKeyboardButton(text=f"📂 {name_of(p, lang)}", callback_data=f"ord:panel:{p.id}"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="nav:main"))

    await cb.message.edit_text(get_text(lang, "select_panel"), reply_markup=kb.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("ord:panel:"))
async def select_panel(cb: CallbackQuery, session: AsyncSession, lang: str):
    """Show categories of selected panel."""
    panel_id = int(cb.data.split(":")[2])
    panel = await session.get(Panel, panel_id)
    if not panel:
        await cb.answer("❌", show_alert=True)
        return

    r = await session.execute(
        select(Category).where(Category.panel_id == panel_id, Category.is_active == True).order_by(Category.sort_order)
    )
    cats = r.scalars().all()

    if not cats:
        await cb.message.edit_text(get_text(lang, "no_categories"), reply_markup=back_kb(lang, "ord:new").as_markup())
        await cb.answer()
        return

    kb = InlineKeyboardBuilder()
    for c in cats:
        kb.row(InlineKeyboardButton(text=f"📁 {name_of(c, lang)}", callback_data=f"ord:cat:{c.id}"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="ord:new"))

    await cb.message.edit_text(get_text(lang, "select_category", panel_name=name_of(panel, lang)), reply_markup=kb.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("ord:cat:"))
async def select_category(cb: CallbackQuery, session: AsyncSession, lang: str):
    """Show services of selected category."""
    cat_id = int(cb.data.split(":")[2])
    cat = await session.get(Category, cat_id)
    if not cat:
        await cb.answer("❌", show_alert=True)
        return

    r = await session.execute(
        select(Service).where(Service.category_id == cat_id, Service.status == "active").order_by(Service.sort_order)
    )
    svcs = r.scalars().all()

    if not svcs:
        await cb.message.edit_text(get_text(lang, "no_services"), reply_markup=back_kb(lang, f"ord:panel:{cat.panel_id}").as_markup())
        await cb.answer()
        return

    kb = InlineKeyboardBuilder()
    for s in svcs:
        price_str = fmt(s.price)
        kb.row(InlineKeyboardButton(text=f"🔹 {name_of(s, lang)} — {price_str}", callback_data=f"ord:svc:{s.id}"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data=f"ord:cat:{cat_id}"))

    await cb.message.edit_text(get_text(lang, "select_service", cat_name=name_of(cat, lang)), reply_markup=kb.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("ord:svc:"))
async def select_service(cb: CallbackQuery, session: AsyncSession, state: FSMContext, lang: str):
    """Show service details and ask for quantity."""
    service_id = int(cb.data.split(":")[2])
    service = await session.get(Service, service_id)
    if not service:
        await cb.answer("❌", show_alert=True)
        return

    await state.update_data(service_id=service_id)

    text = get_text(lang, "service_info",
        name=name_of(service, lang),
        price=fmt(service.price),
        min=service.min_quantity,
        max=service.max_quantity,
    )
    await cb.message.edit_text(text)
    await state.set_state(OrderState.quantity)
    await cb.answer()


@router.message(OrderState.quantity)
async def order_quantity(msg: Message, session: AsyncSession, state: FSMContext, user: User, lang: str):
    """Process quantity input."""
    try:
        raw = msg.text.replace(",", "").replace(" ", "")
        quantity = int(raw)
        data = await state.get_data()
        service = await session.get(Service, data.get("service_id"))

        if not service:
            await msg.answer("⚠️")
            await state.clear()
            return

        if quantity < service.min_quantity or quantity > service.max_quantity:
            await msg.answer(f"⚠️ {service.min_quantity} — {service.max_quantity}")
            return

        total_cost = int((quantity * service.price) / 1000)
        await state.update_data(quantity=quantity, total_cost=total_cost)

        if user.wallet_balance < total_cost:
            await msg.answer(get_text(lang, "insufficient_balance", cost=fmt(total_cost), balance=fmt(user.wallet_balance)))
            await state.clear()
            return

        await msg.answer(get_text(lang, "order_summary",
            service=name_of(service, lang),
            quantity=quantity,
            cost=fmt(total_cost),
        ))
        await state.set_state(OrderState.form_data)
    except (ValueError, AttributeError):
        await msg.answer(get_text(lang, "invalid_number"))


@router.message(OrderState.form_data)
async def order_submit(msg: Message, session: AsyncSession, state: FSMContext, user: User, lang: str):
    """Submit order — deduct balance, create order."""
    data = await state.get_data()
    service_id = data.get("service_id")
    quantity = data.get("quantity")
    total_cost = data.get("total_cost")

    if not all([service_id, quantity, total_cost]):
        await msg.answer("⚠️")
        await state.clear()
        return

    service = await session.get(Service, service_id)
    if not service:
        await msg.answer("⚠️")
        await state.clear()
        return

    # Deduct balance
    balance_before = user.wallet_balance
    user.wallet_balance -= total_cost
    user.total_spent += total_cost
    user.total_orders += 1
    user.update_loyalty()

    # Create order
    order = Order(
        user_id=user.tg_id,
        service_id=service_id,
        quantity=quantity,
        price_per_1000=service.price,
        total_cost=total_cost,
        paid_amount=total_cost,
        form_data=msg.text,
        status=OrderStatus.PENDING,
    )
    session.add(order)

    # Record transaction
    tx = Transaction(
        user_id=user.tg_id,
        order_id=order.id,
        type=TransactionType.PURCHASE,
        amount=-total_cost,
        balance_before=balance_before,
        balance_after=user.wallet_balance,
        description=f"Order #{order.id}",
    )
    session.add(tx)
    await session.flush()

    await msg.answer(get_text(lang, "order_success",
        id=order.id,
        status=order.status.value,
        cost=fmt(total_cost),
    ), reply_markup=main_menu_kb(lang).as_markup())
    await state.clear()


@router.callback_query(F.data == "ord:my")
async def my_orders(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    """Show user's orders."""
    r = await session.execute(
        select(Order)
        .where(Order.user_id == user.tg_id)
        .order_by(desc(Order.created_at))
        .limit(15)
    )
    orders = r.scalars().all()

    if not orders:
        text = get_text(lang, "no_orders")
    else:
        status_emoji = {
            "pending": "⏳", "processing": "🔄", "completed": "✅",
            "rejected": "❌", "cancelled": "🚫", "refunded": "↩️",
            "partially_completed": "⚡️",
        }
        lines = [f"📋 <b>{get_text(lang, 'my_orders_btn')}</b>\n"]
        for o in orders:
            e = status_emoji.get(o.status.value, "📦")
            lines.append(f"{e} <b>#{o.id}</b> | {o.status.value} | {fmt(o.total_cost)}")
        text = "\n".join(lines)

    await cb.message.edit_text(text, reply_markup=back_kb(lang).as_markup(), parse_mode="HTML")
    await cb.answer()
