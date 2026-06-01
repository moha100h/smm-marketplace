"""Order flow — service selection, form filling, payment, tracking."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.panel import Panel, Category, Service
from app.models.order import Order, OrderStatus
from app.models.order_form import OrderForm, FieldType
from app.models.user import User
from app.bot.keyboards.menus import back_btn, main_menu_kb
from app.services.jalali import fmt_price
from app.core.config import settings

router = Router()


class OrderFSM(StatesGroup):
    select_panel = State()
    select_category = State()
    select_service = State()
    fill_form = State()
    enter_quantity = State()
    enter_link = State()
    confirm_order = State()


# ── Navigation ────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "nav:main")
async def nav_main(cb: CallbackQuery, session: AsyncSession):
    """Back to main menu from anywhere."""
    await cb.message.delete()
    user = await session.get(User, cb.from_user.id)
    lang = user.language if user else "fa"
    is_admin = cb.from_user.id in settings.admin_ids_list
    await cb.bot.send_message(
        cb.from_user.id,
        "🏠 منوی اصلی" if lang == "fa" else "🏠 Main Menu",
        reply_markup=main_menu_kb(is_admin=is_admin, lang=lang),
    )
    await cb.answer()


@router.callback_query(F.data == "ord:panels")
async def ord_panels(cb: CallbackQuery, session: AsyncSession, state: FSMContext):
    """Back to panel list."""
    await state.clear()
    r = await session.execute(select(Panel).where(Panel.is_active == True).order_by(Panel.sort_order))
    panels = r.scalars().all()

    kb = InlineKeyboardBuilder()
    for p in panels:
        kb.row(InlineKeyboardButton(text=f"📦 {p.name}", callback_data=f"ord:panel:{p.id}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main"))

    await cb.message.edit_text("📦 پنل مورد نظر را انتخاب کنید:", reply_markup=kb.as_markup())
    await cb.answer()


# ── My Orders ─────────────────────────────────────────────────────────────────
@router.message(F.text.in_(["📋 سفارشات من", "📋 My Orders"]))
async def my_orders(msg: Message, session: AsyncSession):
    """Show user's recent orders."""
    r = await session.execute(
        select(Order)
        .where(Order.user_id == msg.from_user.id)
        .order_by(Order.created_at.desc())
        .limit(10)
    )
    orders = r.scalars().all()

    if not orders:
        await msg.answer("📋 هنوز سفارشی ثبت نکردید / No orders yet")
        return

    status_emoji = {
        OrderStatus.PENDING: "⏳",
        OrderStatus.ACCEPTED: "✅",
        OrderStatus.PROCESSING: "🔄",
        OrderStatus.COMPLETED: "💈",
        OrderStatus.REJECTED: "❌",
        OrderStatus.CANCELLED: "🚫",
        OrderStatus.REFUNDED: "💰",
        OrderStatus.PARTIALLY_COMPLETED: "⚠️",
        OrderStatus.AWAITING_REVIEW: "🔍",
    }

    lines = ["📋 <b>سفارشات اخیر / Recent Orders</b>\n"]
    for o in orders:
        emoji = status_emoji.get(o.status, "📦")
        lines.append(f"{emoji} <b>#{o.id}</b> — {o.quantity:,} — {fmt_price(o.total_cost)} — {o.status.value}")

    text = "\n".join(lines)
    await msg.answer(text, parse_mode="HTML")


# ── Order Flow ────────────────────────────────────────────────────────────────
@router.message(F.text.in_(["🛒 ثبت سفارش", "🛒 New Order"]))
async def start_order(msg: Message, session: AsyncSession, state: FSMContext):
    """Start order flow — show panels."""
    r = await session.execute(select(Panel).where(Panel.is_active == True).order_by(Panel.sort_order))
    panels = r.scalars().all()
    if not panels:
        await msg.answer("⚠️ هیچ پنلی فعال نیست / No active panels")
        return

    kb = InlineKeyboardBuilder()
    for p in panels:
        kb.row(InlineKeyboardButton(text=f"📦 {p.name}", callback_data=f"ord:panel:{p.id}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت / Back", callback_data="nav:main"))

    await state.set_state(OrderFSM.select_panel)
    await msg.answer("📦 پنل مورد نظر را انتخاب کنید / Select a panel:", reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("ord:panel:"))
async def select_panel(cb: CallbackQuery, session: AsyncSession, state: FSMContext):
    panel_id = int(cb.data.split(":")[2])
    await state.update_data(panel_id=panel_id)

    r = await session.execute(
        select(Category).where(Category.panel_id == panel_id, Category.is_active == True).order_by(Category.sort_order)
    )
    categories = r.scalars().all()

    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.row(InlineKeyboardButton(text=f"📂 {c.name}", callback_data=f"ord:cat:{c.id}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="ord:panels"))

    await state.set_state(OrderFSM.select_category)
    await cb.message.edit_text("📂 دسته‌بندی را انتخاب کنید / Select a category:", reply_markup=kb.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("ord:cat:"))
async def select_category(cb: CallbackQuery, session: AsyncSession, state: FSMContext):
    cat_id = int(cb.data.split(":")[2])
    await state.update_data(category_id=cat_id)

    r = await session.execute(
        select(Service).where(Service.category_id == cat_id, Service.status == "active").order_by(Service.sort_order)
    )
    services = r.scalars().all()

    kb = InlineKeyboardBuilder()
    for s in services:
        kb.row(InlineKeyboardButton(
            text=f"✂️ {s.name} — {fmt_price(s.price)}",
            callback_data=f"ord:svc:{s.id}"
        ))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data=f"ord:panel:{await state.get_value('panel_id')}"))

    await state.set_state(OrderFSM.select_service)
    await cb.message.edit_text("✂️ خدمت را انتخاب کنید / Select a service:", reply_markup=kb.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("ord:svc:"))
async def select_service(cb: CallbackQuery, session: AsyncSession, state: FSMContext):
    svc_id = int(cb.data.split(":")[2])
    svc = await session.get(Service, svc_id)
    if not svc:
        await cb.answer("یافت نشد / Not found", show_alert=True)
        return

    await state.update_data(service_id=svc_id, price=svc.price, min_qty=svc.min_quantity, max_qty=svc.max_quantity)

    # Check for custom form fields
    r = await session.execute(select(OrderForm).where(OrderForm.service_id == svc_id).order_by(OrderForm.sort_order))
    forms = r.scalars().all()

    if forms:
        field = forms[0]
        await state.update_data(form_fields=[f.id for f in forms], current_field_idx=0, form_answers={})
        await state.set_state(OrderFSM.fill_form)
        label = field.field_label
        await cb.message.edit_text(f"📝 {label}:", reply_markup=back_btn("nav:main"))
    else:
        await _ask_quantity(cb, state, svc)

    await cb.answer()


async def _ask_quantity(cb_or_msg, state: FSMContext, svc=None):
    d = await state.get_data()
    min_q = d.get("min_qty", 1)
    max_q = d.get("max_qty", 100000)
    await state.set_state(OrderFSM.enter_quantity)
    text = f"🔢 تعداد را وارد کنید (حداقل {min_q}، حداکثر {max_q}):"
    if hasattr(cb_or_msg, "message"):
        await cb_or_msg.message.edit_text(text, reply_markup=back_btn("nav:main"))
    else:
        await cb_or_msg.answer(text)


@router.message(OrderFSM.enter_quantity)
async def enter_quantity(msg: Message, state: FSMContext, session: AsyncSession):
    try:
        qty = int(msg.text.strip().replace(",", "").replace("،", ""))
    except ValueError:
        await msg.answer("❌ عدد معتبر وارد کنید / Enter a valid number")
        return

    d = await state.get_data()
    min_q, max_q = d.get("min_qty", 1), d.get("max_qty", 100000)
    if qty < min_q or qty > max_q:
        await msg.answer(f"❌ تعداد باید بین {min_q} و {max_q} باشد")
        return

    await state.update_data(quantity=qty)

    # Ask for link
    await state.set_state(OrderFSM.enter_link)
    await msg.answer("🔗 لینک را وارد کنید / Enter the link:", reply_markup=back_btn("nav:main"))


@router.message(OrderFSM.enter_link)
async def enter_link(msg: Message, state: FSMContext, session: AsyncSession):
    link = msg.text.strip()
    await state.update_data(link=link)

    d = await state.get_data()
    qty = d["quantity"]
    price = d["price"]
    total = (qty * price) // 1000

    # Check wallet
    user = await session.get(User, msg.from_user.id)
    can_pay = user.wallet_balance >= total if user else False

    text = (
        f"📋 <b>خلاصه سفارش / Order Summary</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔢 تعداد: <b>{qty:,}</b>\n"
        f"💰 قیمت: <b>{fmt_price(total)}</b>\n"
        f"🔗 لینک: <code>{link}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💰 موجودی کیف پول: <b>{fmt_price(user.wallet_balance)}</b>\n"
    )

    kb = InlineKeyboardBuilder()
    if can_pay:
        kb.row(InlineKeyboardButton(text="✅ تایید و پرداخت / Confirm & Pay", callback_data="ord:confirm:pay"))
    else:
        kb.row(InlineKeyboardButton(text="💳 شارژ کیف پول / Top Up Wallet", callback_data="wallet:deposit"))
    kb.row(InlineKeyboardButton(text="🔙 انصراف / Cancel", callback_data="nav:main"))

    await state.set_state(OrderFSM.confirm_order)
    await msg.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "ord:confirm:pay")
async def confirm_order(cb: CallbackQuery, state: FSMContext, session: AsyncSession):
    d = await state.get_data()
    user = await session.get(User, cb.from_user.id)
    total = (d["quantity"] * d["price"]) // 1000

    if user.wallet_balance < total:
        await cb.answer("موجودی کافی نیست / Insufficient balance", show_alert=True)
        return

    # Deduct wallet
    user.wallet_balance -= total
    user.total_spent += total
    user.total_orders += 1
    user.update_loyalty()

    # Create order
    order = Order(
        user_id=cb.from_user.id,
        service_id=d["service_id"],
        quantity=d["quantity"],
        price_per_1000=d["price"],
        total_cost=total,
        paid_amount=total,
        form_data=d.get("link", ""),
        status=OrderStatus.PENDING,
    )
    session.add(order)
    await session.flush()

    await state.clear()
    await cb.message.edit_text(
        f"✅ سفارش #{order.id} ثبت شد!\n\nوضعیت: ⏳ در انتظار بررسی",
        reply_markup=back_btn("nav:main"),
    )
    await cb.answer()
