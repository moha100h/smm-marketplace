"""Services browsing handler."""
from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.panel import Panel, Category, Service
from app.services.jalali import fmt_price

router = Router()


@router.message(F.text.in_(["📦 خدمات", "📦 Services"]))
async def browse_services(msg: Message, session: AsyncSession):
    r = await session.execute(select(Panel).where(Panel.is_active == True).order_by(Panel.sort_order))
    panels = r.scalars().all()

    if not panels:
        await msg.answer("⚠️ هیچ خدماتی فعال نیست / No active services")
        return

    lines = ["📦 <b>لیست خدمات / Services</b>
"]
    for panel in panels:
        lines.append(f"
📁 <b>{panel.name}</b>")
        for cat in panel.categories:
            if not cat.is_active:
                continue
            lines.append(f"  📂 {cat.name}")
            for svc in cat.services:
                if svc.status.value == "active":
                    lines.append(f"    ✂️ {svc.name} — {fmt_price(svc.price)} / 1000")

    await msg.answer("
".join(lines), parse_mode="HTML")
