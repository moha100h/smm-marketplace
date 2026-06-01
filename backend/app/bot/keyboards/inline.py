"""Inline keyboard builder — clean, professional."""
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from app.core.i18n import get_text


def main_menu_kb(lang: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text=get_text(lang, "new_order_btn"), callback_data="ord:new"),
        InlineKeyboardButton(text=get_text(lang, "my_orders_btn"), callback_data="ord:my"),
    )
    kb.row(
        InlineKeyboardButton(text=get_text(lang, "wallet_btn"), callback_data="wallet:main"),
    )
    kb.row(
        InlineKeyboardButton(text=get_text(lang, "referral_btn"), callback_data="referral:main"),
        InlineKeyboardButton(text=get_text(lang, "support_btn"), callback_data="support:main"),
    )
    kb.row(
        InlineKeyboardButton(text=get_text(lang, "settings_btn"), callback_data="set:main"),
    )
    return kb


def main_menu_with_admin_kb(lang: str) -> InlineKeyboardBuilder:
    """Main menu with admin button for admins."""
    kb = main_menu_kb(lang)
    kb.row(
        InlineKeyboardButton(text=get_text(lang, "admin_btn"), callback_data="admin:main"),
    )
    return kb


def wallet_menu_kb(lang: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text=get_text(lang, "deposit_btn"), callback_data="wallet:deposit"),
        InlineKeyboardButton(text=get_text(lang, "transactions_btn"), callback_data="wallet:tx"),
    )
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="nav:main"))
    return kb


def back_kb(lang: str, callback: str = "nav:main") -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data=callback))
    return kb


def admin_menu_kb(lang: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="\U0001f4ca آمار / Stats", callback_data="admin:stats"),
        InlineKeyboardButton(text="\U0001f4b3 واریزها / Deposits", callback_data="admin:deposits"),
    )
    kb.row(
        InlineKeyboardButton(text="\U0001f4e6 سفارشات / Orders", callback_data="admin:orders"),
        InlineKeyboardButton(text="\U0001f465 کاربران / Users", callback_data="admin:users"),
    )
    kb.row(
        InlineKeyboardButton(text="\U0001f3ab تیکت‌ها / Tickets", callback_data="admin:tickets"),
    )
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="nav:main"))
    return kb


def lang_select_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="\U0001f1ee\U0001f1f7 فارسی", callback_data="set:lang:fa"),
        InlineKeyboardButton(text="\U0001f1ec\U0001f1e7 English", callback_data="set:lang:en"),
    )
    kb.row(InlineKeyboardButton(text="\u25c0\ufe0f بازگشت / Back", callback_data="nav:main"))
    return kb


def settings_kb(lang: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="\U0001f310 تغییر زبان / Change Language", callback_data="set:lang"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="nav:main"))
    return kb


def support_kb(lang: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="\U0001f4dd ارسال تیکت / Send Ticket", callback_data="ticket:new"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="nav:main"))
    return kb
