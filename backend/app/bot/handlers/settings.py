"""Settings handler — language, profile."""
from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.bot.keyboards.inline import settings_kb, lang_select_kb, back_kb, main_menu_kb
from app.core.i18n import get_text

router = Router()


@router.callback_query(F.data == "set:main")
async def settings_main(cb: CallbackQuery, lang: str):
    text = get_text(lang, "settings_title")
    await cb.message.edit_text(text, reply_markup=settings_kb(lang).as_markup())
    await cb.answer()


@router.callback_query(F.data == "set:lang")
async def change_lang(cb: CallbackQuery, lang: str):
    text = get_text(lang, "settings_lang", lang="فارسی" if lang == "fa" else "English")
    await cb.message.edit_text(text, reply_markup=lang_select_kb().as_markup())
    await cb.answer()
