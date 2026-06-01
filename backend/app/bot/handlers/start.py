"""Start handler — /start, registration, language, main menu."""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.bot.keyboards.inline import main_menu_kb, lang_select_kb
from app.core.i18n import get_text
from app.core.config import settings

router = Router()


@router.message(Command("start"))
async def cmd_start(msg: Message, session: AsyncSession, user: User, lang: str):
    """Handle /start — show language picker for new users, main menu for existing."""
    # Check if this is a fresh registration (no language set yet)
    if user.language == "fa" and not user.full_name:
        # Brand new user — show language selection
        welcome = get_text("fa", "welcome")
        await msg.answer(welcome, reply_markup=lang_select_kb().as_markup())
        return

    # Existing user — show main menu
    name = user.full_name or msg.from_user.full_name or ""
    text = get_text(lang, "welcome_back", name=name)
    await msg.answer(text, reply_markup=main_menu_kb(lang).as_markup())


@router.callback_query(F.data == "nav:main")
async def show_main_menu(cb: CallbackQuery, session: AsyncSession, user: User, lang: str):
    """Show main menu."""
    text = get_text(lang, "main_menu")
    await cb.message.edit_text(text, reply_markup=main_menu_kb(lang).as_markup())
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

        text = get_text(new_lang, "lang_changed")
        await cb.message.edit_text(text, reply_markup=main_menu_kb(new_lang).as_markup())
        await cb.answer()
    else:
        # Show language selection
        await cb.message.edit_text(
            "🌐 زبان / Language\n\nزبان خود را انتخاب کنید:\nSelect your language:",
            reply_markup=lang_select_kb().as_markup(),
        )
        await cb.answer()
