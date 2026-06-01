"""Start command, registration, language selection, main menu."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
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
        user.registered_at = user.registered_at or __import__("datetime").datetime.utcnow()
        await session.flush()

    await state.clear()
    is_admin = msg.from_user.id in settings.admin_ids_list
    lang = user.language if user else "fa"
    welcome = f"🎉 ثبت‌نام کامل شد!

👤 <b>{name}</b>" if lang == "fa" else f"🎉 Registration complete!

👤 <b>{name}</b>"
    await msg.answer(welcome, reply_markup=main_menu_kb(is_admin=is_admin, lang=lang))
