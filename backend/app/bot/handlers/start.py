"""Start handler — /start, registration, main menu."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.bot.keyboards.menus import main_menu_kb
from app.core.config import settings

router = Router()


@router.message(Command("start"))
async def cmd_start(msg: Message, session: AsyncSession):
    """Handle /start command."""
    tg_id = msg.from_user.id
    user = await session.get(User, tg_id)

    if not user:
        # Check referral
        ref_code = None
        if msg.text and len(msg.text.split()) > 1:
            ref_code = msg.text.split()[1]

        user = User(
            tg_id=tg_id,
            username=msg.from_user.username,
            full_name=msg.from_user.full_name,
        )

        if ref_code:
            r = await session.execute(select(User).where(User.referral_code == ref_code))
            referrer = r.scalar_one_or_none()
            if referrer:
                user.referred_by_id = referrer.id

        session.add(user)
        await session.flush()
        welcome = f"🎉 خوش آمدید {msg.from_user.full_name or 'کاربر'}!\n\nبه مارکت‌پلیس SMM خوش آمدید."
    else:
        welcome = f"👋 سلام {user.full_name or 'کاربر'}! خوش برگشتید."

    await msg.answer(welcome, reply_markup=main_menu_kb().as_markup())


@router.message(F.text == "🏠 منوی اصلی")
@router.callback_query(F.data == "nav:main")
async def show_main_menu(event, session: AsyncSession):
    """Show main menu."""
    if isinstance(event, CallbackQuery):
        await event.message.edit_text("🏠 منوی اصلی:", reply_markup=main_menu_kb().as_markup())
        await event.answer()
    else:
        await event.answer("🏠 منوی اصلی:", reply_markup=main_menu_kb().as_markup())


@router.callback_query(F.data == "support:main")
async def support_main(cb: CallbackQuery):
    """Show support info."""
    admin_ids = settings.admin_ids_list
    admin_links = ", ".join([f"tg://user?id={aid}" for aid in admin_ids])
    await cb.message.edit_text(
        f"🎫 پشتیبانی\n\nبرای ارتباط با ادمین:\n{admin_links}",
        reply_markup=main_menu_kb().as_markup(),
    )
    await cb.answer()


@router.callback_query(F.data == "referral:main")
async def referral_main(cb: CallbackQuery, session: AsyncSession):
    """Show referral info."""
    user = await session.get(User, cb.from_user.id)
    if not user:
        await cb.answer("کاربر یافت نشد", show_alert=True)
        return

    if not user.referral_code:
        import secrets
        user.referral_code = secrets.token_hex(6)
        await session.flush()

    ref_link = f"https://t.me/{(await cb.bot.get_me()).username}?start={user.referral_code}"
    await cb.message.edit_text(
        f"🎁 دعوت دوستان\n\nلینک دعوت شما:\n`{ref_link}`\n\n"
        f"با هر دعوت {settings.REFERRAL_COMMISSION_PERCENT}% پاداش بگیرید!",
        reply_markup=main_menu_kb().as_markup(),
    )
    await cb.answer()


@router.callback_query(F.data == "set:main")
async def settings_main(cb: CallbackQuery):
    """Show settings menu."""
    await cb.message.edit_text(
        "⚙️ تنظیمات\n\nبه زودی...",
        reply_markup=main_menu_kb().as_markup(),
    )
    await cb.answer()
