"""Referral handler — invite friends, earn commission."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User
from app.bot.keyboards.inline import back_kb
from app.core.i18n import get_text
from app.core.config import settings

router = Router()


@router.callback_query(F.data == "referral:main")
async def referral_main(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    """Show referral info."""
    # Count referrals
    r = await session.execute(select(func.count(User.id)).where(User.referred_by_id == user.id))
    referral_count = r.scalar() or 0

    link = f"https://t.me/{(await cb.bot.get_me()).username}?start={user.referral_code}"
    percent = settings.REFERRAL_COMMISSION_PERCENT

    text = get_text(lang, "referral_info",
        link=link,
        percent=percent,
        count=referral_count,
    )
    await cb.message.edit_text(text, reply_markup=back_kb(lang).as_markup())
    await cb.answer()
