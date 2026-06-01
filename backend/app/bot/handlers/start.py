"""Start handler — /start, registration, language, main menu."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.bot.keyboards.inline import main_menu_kb, lang_select_kb, main_menu_with_admin_kb
from app.core.i18n import get_text
from app.core.config import settings

router = Router()


@router.message(Command("start"))
async def cmd_start(msg: Message, session: AsyncSession, user: User, lang: str):
    """Handle /start — show language picker for new users, main menu for existing."""
    # Check if user was JUST created (no language set = brand new)
    if user.language is None or user.language == "fa" and user.registered_at == user.last_active_at:
        # Brand new user — show language selection
        welcome = get_text("fa", "welcome")
        await msg.answer(welcome, reply_markup=lang_select_kb().as_markup())
        return

    # Existing user — show main menu
    name = user.full_name or msg.from_user.full_name or ""
    text = get_text(lang, "welcome_back", name=name)
    is_admin = user.is_admin or user.tg_id in settings.admin_ids_list
    kb = main_menu_with_admin_kb(lang) if is_admin else main_menu_kb(lang)
    await msg.answer(text, reply_markup=kb.as_markup())


@router.callback_query(F.data == "nav:main")
async def show_main_menu(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    """Show main menu."""
    text = get_text(lang, "main_menu")
    is_admin = user.is_admin or user.tg_id in settings.admin_ids_list
    kb = main_menu_with_admin_kb(lang) if is_admin else main_menu_kb(lang)
    await cb.message.edit_text(text, reply_markup=kb.as_markup())
    await cb.answer()


@router.callback_query(F.data == "admin:main")
async def go_admin(cb: CallbackQuery, user: User, lang: str):
    """Go to admin panel from main menu."""
    if not (user.is_admin or user.tg_id in settings.admin_ids_list):
        await cb.answer("⛔️", show_alert=True)
        return
    from app.bot.keyboards.inline import admin_menu_kb
    await cb.message.edit_text(get_text(lang, "admin_menu"), reply_markup=admin_menu_kb(lang).as_markup())
    await cb.answer()


@router.callback_query(F.data.startswith("set:lang"))
async def select_language(cb: CallbackQuery, session: AsyncSession, user: User):
    """Handle language selection."""
    parts = cb.data.split(":")
    if len(parts) == 3:
        # User selected a language
        new_lang = parts[2]
        user.language = new_lang
        await session.flush()

        from app.bot.keyboards.inline import main_menu_kb, main_menu_with_admin_kb
        from app.core.config import settings
        is_admin = user.is_admin or user.tg_id in settings.admin_ids_list
        kb = main_menu_with_admin_kb(new_lang) if is_admin else main_menu_kb(new_lang)

        text = get_text(new_lang, "lang_changed")
        await cb.message.edit_text(text, reply_markup=kb.as_markup())
        await cb.answer()
    else:
        # Show language selection
        await cb.message.edit_text(
            "\U0001f310 زبان / Language\n\nزبان خود را انتخاب کنید:\nSelect your language:",
            reply_markup=lang_select_kb().as_markup(),
        )
        await cb.answer()
