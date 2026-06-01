"""All keyboard builders — user & admin menus."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def language_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="lang:fa"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
    )
    return kb.as_markup()


def main_menu_kb(is_admin: bool = False, lang: str = "fa") -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    if lang == "fa":
        kb.row(KeyboardButton(text="🛒 ثبت سفارش"))
        kb.row(KeyboardButton(text="📦 خدمات"))
        kb.row(KeyboardButton(text="📋 سفارشات من"))
        kb.row(KeyboardButton(text="💰 کیف پول"))
        kb.row(KeyboardButton(text="🎟 کد تخفیف"))
        kb.row(KeyboardButton(text="🎁 دعوت دوستان"))
        kb.row(KeyboardButton(text="🎫 پشتیبانی"))
        if is_admin:
            kb.row(KeyboardButton(text="⚙️ پنل مدیریت"))
    else:
        kb.row(KeyboardButton(text="🛒 New Order"))
        kb.row(KeyboardButton(text="📦 Services"))
        kb.row(KeyboardButton(text="📋 My Orders"))
        kb.row(KeyboardButton(text="💰 Wallet"))
        kb.row(KeyboardButton(text="🎟 Discount Code"))
        kb.row(KeyboardButton(text="🎁 Referral"))
        kb.row(KeyboardButton(text="🎫 Support"))
        if is_admin:
            kb.row(KeyboardButton(text="⚙️ Admin Panel"))
    return kb.as_markup(resize_keyboard=True)


def back_btn(callback: str = "nav:main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔙 بازگشت / Back", callback_data=callback)
    ]])
