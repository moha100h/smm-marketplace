"""Inline keyboard builders for bot menus."""
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

back_btn = InlineKeyboardButton(text="🔙 بازگشت / Back", callback_data="nav:main")


def main_menu_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="📦 خدمات / Services", callback_data="svc:main"))
    kb.row(InlineKeyboardButton(text="🛒 سفارش جدید / New Order", callback_data="ord:new"))
    kb.row(InlineKeyboardButton(text="📋 سفارشات من / My Orders", callback_data="ord:my"))
    kb.row(InlineKeyboardButton(text="💰 کیف پول / Wallet", callback_data="wallet:main"))
    kb.row(InlineKeyboardButton(text="🎫 پشتیبانی / Support", callback_data="support:main"))
    kb.row(InlineKeyboardButton(text="🎁 دعوت دوستان / Referral", callback_data="referral:main"))
    kb.row(InlineKeyboardButton(text="⚙️ تنظیمات / Settings", callback_data="set:main"))
    return kb


def wallet_menu_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="💳 افزایش موجودی / Deposit", callback_data="wallet:deposit"))
    kb.row(InlineKeyboardButton(text="📊 تراکنش‌ها / Transactions", callback_data="wallet:tx"))
    kb.row(back_btn)
    return kb


def order_status_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="⏳ در انتظار / Pending", callback_data="ord:status:pending"))
    kb.row(InlineKeyboardButton(text="✅ تکمیل شده / Completed", callback_data="ord:status:completed"))
    kb.row(InlineKeyboardButton(text="❌ لغو شده / Cancelled", callback_data="ord:status:cancelled"))
    kb.row(back_btn)
    return kb
