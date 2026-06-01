"""Start command, registration, language selection, main menu."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.bot.keyboards.menus import main_menu_kb, language_kb
from app.core.config import settings
import secrets

router = Router()


class RegFSM(StatesGroup):
    phone = State()
    full_name = State()


def _generate_referral_code() -> str:
    return secrets.token_urlsafe(6).upper()


@router.message(CommandStart())
async def cmd_start(msg: Message, session: AsyncSession, state: FSMContext):
    await state.clear()

    # Check for referral
    args = msg.text.split()
    referral_code = args[1] if len(args) > 1 else None

    # Check if user exists
    user = await session.get(User, msg.from_user.id)
    if not user:
        user = User(
            tg_id=msg.from_user.id,
            username=msg.from_user.username,
            language="fa",
            referral_code=_generate_referral_code(),
        )
        session.add(user)
        await session.flush()

        # Handle referral
        if referral_code:
            from sqlalchemy import select
            stmt = select(User).where(User.referral_code == referral_code)
            result = await session.execute(stmt)
            referrer = result.scalar_one_or_none()
            if referrer:
                user.referred_by_id = referrer.id

    if not user.registered_at or not user.full_name:
        # Show language selection first
        await msg.answer(
            "🌐 زبان خود را انتخاب کنید / Choose your language:",
            reply_markup=language_kb(),
        )
        return

    # Show main menu
    is_admin = msg.from_user.id in settings.admin_ids_list
    await msg.answer(
        f"👋 خوش آمدید <b>{user.full_name}</b>!",
        reply_markup=main_menu_kb(is_admin=is_admin, lang=user.language),
    )


@router.callback_query(F.data.startswith("lang:"))
async def set_language(cb: CallbackQuery, session: AsyncSession, state: FSMContext):
    lang = cb.data.split(":")[1]
    user = await session.get(User, cb.from_user.id)
    if user:
        user.language = lang
        await session.flush()

    if not user.full_name:
        await state.set_state(RegFSM.full_name)
        prompt = "👤 نام و نام خانوادگی خود را وارد کنید:" if lang == "fa" else "👤 Enter your full name:"
        await cb.message.edit_text(prompt)
    else:
        await cb.message.delete()
        is_admin = cb.from_user.id in settings.admin_ids_list
        await cb.bot.send_message(
            cb.from_user.id,
            "🏠" if lang == "fa" else "🏠 Main Menu",
            reply_markup=main_menu_kb(is_admin=is_admin, lang=lang),
        )
    await cb.answer()


@router.message(RegFSM.full_name)
async def reg_full_name(msg: Message, state: FSMContext, session: AsyncSession):
    name = msg.text.strip()
    if len(name) < 2:
        await msg.answer("❌ نام باید حداقل ۲ حرف باشد / Name must be at least 2 characters")
        return

    user = await session.get(User, msg.from_user.id)
    if user:
        user.full_name = name
        from datetime import datetime
        user.registered_at = user.registered_at or datetime.utcnow()
        await session.flush()

    await state.clear()
    is_admin = msg.from_user.id in settings.admin_ids_list
    lang = user.language if user else "fa"
    welcome = f"🎉 ثبت‌نام کامل شد!\n\n👤 <b>{name}</b>" if lang == "fa" else f"🎉 Registration complete!\n\n👤 <b>{name}</b>"
    await msg.answer(welcome, reply_markup=main_menu_kb(is_admin=is_admin, lang=lang))


# ── Missing button handlers ──────────────────────────────────────────────────
@router.message(F.text.in_(["🎟 کد تخفیف", "🎟 Discount Code"]))
async def discount_code(msg: Message):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main"))
    await msg.answer(
        "🎟 <b>کد تخفیف / Discount Code</b>\n\nکد تخفیف خود را وارد کنید:",
        reply_markup=kb.as_markup(),
        parse_mode="HTML",
    )


@router.message(F.text.in_(["🎁 دعوت دوستان", "🎁 Referral"]))
async def referral(msg: Message, session: AsyncSession):
    user = await session.get(User, msg.from_user.id)
    if not user or not user.referral_code:
        await msg.answer("⚠️ ابتدا ثبت‌نام کنید")
        return

    from app.core.config import settings
    bot_username = (await msg.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={user.referral_code}"

    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main"))

    await msg.answer(
        f"🎁 <b>دعوت دوستان / Referral</b>\n\n"
        f"لینک دعوت شما:\n<code>{link}</code>\n\n"
        f"با هر دعوت {settings.REFERRAL_COMMISSION_PERCENT}% کمیسیون دریافت می‌کنید!",
        reply_markup=kb.as_markup(),
        parse_mode="HTML",
    )


@router.message(F.text.in_(["🎫 پشتیبانی", "🎫 Support"]))
async def support(msg: Message):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🎫 ارسال تیکت", callback_data="ticket:new"))
    kb.row(InlineKeyboardButton(text="📋 تیکت‌های من", callback_data="ticket:my"))
    kb.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="nav:main"))
    await msg.answer(
        "🎫 <b>پشتیبانی / Support</b>\n\nچطور می‌توانیم کمکتان کنیم؟",
        reply_markup=kb.as_markup(),
        parse_mode="HTML",
    )
