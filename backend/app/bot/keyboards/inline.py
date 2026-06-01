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
        InlineKeyboardButton(text="📊 آمار / Stats", callback_data="admin:stats"),
        InlineKeyboardButton(text="💳 واریزها / Deposits", callback_data="admin:deposits"),
    )
    kb.row(
        InlineKeyboardButton(text="📦 سفارشات / Orders", callback_data="admin:orders"),
        InlineKeyboardButton(text="👥 کاربران / Users", callback_data="admin:users"),
    )
    kb.row(
        InlineKeyboardButton(text="🎫 تیکت‌ها / Tickets", callback_data="admin:tickets"),
        InlineKeyboardButton(text="⚙️ تنظیمات / Settings", callback_data="admin:settings"),
    )
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="nav:main"))
    return kb


def deposit_action_kb(payment_id: int, lang: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text=get_text(lang, "approve_btn"), callback_data=f"admin:dep:approve:{payment_id}"),
        InlineKeyboardButton(text=get_text(lang, "reject_btn"), callback_data=f"admin:dep:reject:{payment_id}"),
    )
    return kb


def order_action_kb(order_id: int, lang: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="✅ تکمیل", callback_data=f"admin:ord:completed:{order_id}"),
        InlineKeyboardButton(text="🔄 در حال انجام", callback_data=f"admin:ord:processing:{order_id}"),
    )
    kb.row(
        InlineKeyboardButton(text="❌ رد", callback_data=f"admin:ord:rejected:{order_id}"),
        InlineKeyboardButton(text="↩️ بازگشت", callback_data=f"admin:ord:refunded:{order_id}"),
    )
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="admin:orders"))
    return kb


def lang_select_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="🇮🇷 فارسی", callback_data="set:lang:fa"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set:lang:en"),
    )
    kb.row(InlineKeyboardButton(text="◀️ بازگشت / Back", callback_data="set:main"))
    return kb


def settings_kb(lang: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="🌐 تغییر زبان / Change Language", callback_data="set:lang"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="nav:main"))
    return kb


def support_kb(lang: str) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📝 ارسال تیکت / Send Ticket", callback_data="ticket:new"))
    kb.row(InlineKeyboardButton(text=get_text(lang, "back"), callback_data="nav:main"))
    return kb
