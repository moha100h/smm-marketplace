"""Services handler — browse services by panel/category."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.panel import Panel, Category, Service
from app.services.jalali import fmt_price
from app.bot.keyboards.menus import back_btn

router = Router()


@router.message(F.text.in_(["📦 خدمات", "📦 Services"]))
async def browse_services(msg: Message, session: AsyncSession):
    r = await session.execute(select(Panel).where(Panel.is_active == True).order_by(Panel.sort_order))
    panels = r.scalars().all()

    if not panels:
        await msg.answer("⚠️ هیچ پنلی فعال نیست / No active panels")
        return

    lines = ["📦 <b>لیست خدمات / Services</b>\n"]
    for p in panels:
        lines.append(f"📂 <b>{p.name}</b> — {p.description or ''}")

    text = "\n".join(lines)

    kb = InlineKeyboardBuilder()
    for p in panels:
        kb.row(InlineKeyboardButton(text=f"📂 {p.name}", callback_data=f"svc:panel:{p.id}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت / Back", callback_data="nav:main"))

    await msg.answer(text, reply_markup=kb.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("svc:panel:"))
async def svc_panel(cb: CallbackQuery, session: AsyncSession):
    panel_id = int(cb.data.split(":")[2])
    r = await session.execute(
        select(Category).where(Category.panel_id == panel_id, Category.is_active == True).order_by(Category.sort_order)
    )
    categories = r.scalars().all()

    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.row(InlineKeyboardButton(text=f"📁 {c.name}", callback_data=f"svc:cat:{c.id}"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main"))

    await cb.message.edit_text("📁 دسته‌بندی‌ها:", reply_markup=kb.as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("svc:cat:"))
async def svc_category(cb: CallbackQuery, session: AsyncSession):
    cat_id = int(cb.data.split(":")[2])
    r = await session.execute(
        select(Service).where(Service.category_id == cat_id, Service.status == "active").order_by(Service.sort_order)
    )
    services = r.scalars().all()

    if not services:
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main"))
        await cb.message.edit_text("⚠️ هیچ خدمتی در این دسته نیست", reply_markup=kb.as_markup())
        await cb.answer()
        return

    lines = ["✂️ <b>خدمات:</b>\n"]
    for s in services:
        lines.append(f"• {s.name} — {fmt_price(s.price)} (min: {s.min_quantity}, max: {s.max_quantity})")

    text = "\n".join(lines)
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main"))
    await cb.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="HTML")
    await cb.answer()
