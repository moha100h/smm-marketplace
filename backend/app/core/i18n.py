"""Internationalization — FA/EN translations."""

TRANSLATIONS = {
    # ── Start / Welcome ──
    "welcome": {
        "fa": "🎉 به مارکت‌پلیس SMM خوش آمدید!\n\nلطفاً زبان خود را انتخاب کنید:",
        "en": "🎉 Welcome to SMM Marketplace!\n\nPlease select your language:",
    },
    "welcome_back": {
        "fa": "👋 سلام {name}! خوش برگشتید.",
        "en": "👋 Hello {name}! Welcome back.",
    },
    "registered": {
        "fa": "✅ ثبت‌نام شما با موفقیت انجام شد!\n\n🎁 هدیه خوش‌آمدگویی: {bonus} تومان به کیف پول شما اضافه شد.",
        "en": "✅ Registration successful!\n\n🎁 Welcome bonus: {bonus} added to your wallet.",
    },
    "referral_used": {
        "fa": "🔗 شما با کد دعوت {code} ثبت‌نام شدید.",
        "en": "🔗 You registered with referral code {code}.",
    },

    # ── Main Menu ──
    "main_menu": {
        "fa": "🏠 منوی اصلی\n\nیکی از گزینه‌ها را انتخاب کنید:",
        "en": "🏠 Main Menu\n\nSelect an option:",
    },

    # ── Wallet ──
    "wallet_title": {
        "fa": "💰 کیف پول",
        "en": "💰 Wallet",
    },
    "wallet_info": {
        "fa": "💰 موجودی: {balance} تومان\n📊 کل خرید: {spent} تومان\n⭐ سطح: {level}\n\n🔢 تعداد سفارشات: {orders}",
        "en": "💰 Balance: {balance}\n📊 Total spent: {spent}\n⭐ Level: {level}\n\n🔢 Orders: {orders}",
    },
    "deposit_amount": {
        "fa": "💳 افزایش موجودی\n\nمبلغ را وارد کنید (تومان):\n\nحداقل: ۱۰,۰۰۰ تومان",
        "en": "💳 Deposit\n\nEnter amount:\n\nMinimum: 10,000",
    },
    "deposit_min": {
        "fa": "⚠️ حداقل مبلغ ۱۰,۰۰۰ تومان است.",
        "en": "⚠️ Minimum amount is 10,000.",
    },
    "deposit_receipt": {
        "fa": "📋 مبلغ: {amount} تومان\n\nلطفاً رسید پرداخت را ارسال کنید (عکس یا متن):",
        "en": "📋 Amount: {amount}\n\nPlease send payment receipt (photo or text):",
    },
    "deposit_sent": {
        "fa": "✅ رسید شما ارسال شد.\n\nپس از بررسی توسط ادمین، موجودی شما افزایش می‌یابد.",
        "en": "✅ Receipt sent.\n\nYour balance will be updated after admin review.",
    },
    "deposit_approved": {
        "fa": "✅ واریز شما تأیید شد!\n\nمبلغ: {amount} تومان\nموجودی جدید: {balance} تومان",
        "en": "✅ Deposit approved!\n\nAmount: {amount}\nNew balance: {balance}",
    },
    "deposit_rejected": {
        "fa": "❌ واریز شما رد شد.\n\nمبلغ: {amount} تومان\nلطفاً با پشتیبانی تماس بگیرید.",
        "en": "❌ Deposit rejected.\n\nAmount: {amount}\nPlease contact support.",
    },
    "no_transactions": {
        "fa": "📊 هنوز تراکنشی ندارید.",
        "en": "📊 No transactions yet.",
    },

    # ── Orders ──
    "select_panel": {
        "fa": "📦 انتخاب پنل:\n\nپنل مورد نظر را انتخاب کنید:",
        "en": "📦 Select Panel:\n\nChoose a panel:",
    },
    "select_category": {
        "fa": "📂 انتخاب دسته‌بندی:\n\n{panel_name}",
        "en": "📂 Select Category:\n\n{panel_name}",
    },
    "select_service": {
        "fa": "🛒 انتخاب خدمت:\n\n{cat_name}",
        "en": "🛒 Select Service:\n\n{cat_name}",
    },
    "service_info": {
        "fa": "📦 {name}\n\n💰 قیمت: {price} تومان (per 1000)\n📏 حداقل: {min}\n📏 حداکثر: {max}\n\nتعداد را وارد کنید:",
        "en": "📦 {name}\n\n💰 Price: {price} (per 1000)\n📏 Min: {min}\n📏 Max: {max}\n\nEnter quantity:",
    },
    "order_summary": {
        "fa": "📋 خلاصه سفارش:\n\n📦 خدمت: {service}\n🔢 تعداد: {quantity}\n💰 هزینه: {cost} تومان\n\nلینک/اطلاعات مورد نیاز را ارسال کنید:",
        "en": "📋 Order Summary:\n\n📦 Service: {service}\n🔢 Quantity: {quantity}\n💰 Cost: {cost}\n\nSend link/required info:",
    },
    "order_success": {
        "fa": "✅ سفارش ثبت شد!\n\n🔢 شماره: #{id}\n📊 وضعیت: {status}\n💰 هزینه: {cost} تومان",
        "en": "✅ Order placed!\n\n🔢 ID: #{id}\n📊 Status: {status}\n💰 Cost: {cost}",
    },
    "insufficient_balance": {
        "fa": "❌ موجودی کافی نیست!\n\n💰 هزینه: {cost} تومان\n💳 موجودی: {balance} تومان\n\nلطفاً ابتدا کیف پول خود را شارژ کنید.",
        "en": "❌ Insufficient balance!\n\n💰 Cost: {cost}\n💳 Balance: {balance}\n\nPlease deposit first.",
    },
    "my_orders": {
        "fa": "📋 سفارشات من",
        "en": "📋 My Orders",
    },
    "no_orders": {
        "fa": "📋 هنوز سفارشی ندارید.",
        "en": "📋 No orders yet.",
    },
    "no_panels": {
        "fa": "⚠️ هیچ پنلی فعال نیست.",
        "en": "⚠️ No active panels.",
    },
    "no_categories": {
        "fa": "⚠️ این پنل دسته‌بندی ندارد.",
        "en": "⚠️ This panel has no categories.",
    },
    "no_services": {
        "fa": "⚠️ این دسته‌بندی خدمتی ندارد.",
        "en": "⚠️ This category has no services.",
    },

    # ── Admin ──
    "admin_menu": {
        "fa": "👑 پنل مدیریت\n\nیکی از گزینه‌ها را انتخاب کنید:",
        "en": "👑 Admin Panel\n\nSelect an option:",
    },
    "admin_stats": {
        "fa": "📊 آمار کلی\n\n👥 کاربران: {users}\n📦 سفارشات: {orders}\n💰 درآمد کل: {revenue} تومان\n💳 در انتظار تأیید: {pending}",
        "en": "📊 Statistics\n\n👥 Users: {users}\n📦 Orders: {orders}\n💰 Revenue: {revenue}\n💳 Pending: {pending}",
    },
    "admin_deposits": {
        "fa": "💳 درخواست‌های واریز",
        "en": "💳 Deposit Requests",
    },
    "admin_orders": {
        "fa": "📦 مدیریت سفارشات",
        "en": "📦 Order Management",
    },
    "no_pending_deposits": {
        "fa": "✅ هیچ درخواست واریزی در انتظار نیست.",
        "en": "✅ No pending deposits.",
    },

    # ── Referral ──
    "referral_title": {
        "fa": "🎁 دعوت دوستان",
        "en": "🎁 Referral Program",
    },
    "referral_info": {
        "fa": "🎁 دعوت دوستان\n\nلینک دعوت شما:\n`{link}`\n\n💰 پاداش: {percent}% از خرید هر زیرمجموعه\n👥 تعداد دعوت: {count} نفر",
        "en": "🎁 Referral Program\n\nYour link:\n`{link}`\n\n💰 Bonus: {percent}% of each referral purchase\n👥 Invited: {count}",
    },

    # ── Support ──
    "support_title": {
        "fa": "🎫 پشتیبانی",
        "en": "🎫 Support",
    },
    "support_info": {
        "fa": "🎫 پشتیبانی\n\nبرای ارتباط با ادمین:\n{admin_links}\n\nیا تیکت ارسال کنید:",
        "en": "🎫 Support\n\nContact admin:\n{admin_links}\n\nOr send a ticket:",
    },
    "ticket_subject": {
        "fa": "📝 موضوع تیکت را وارد کنید:",
        "en": "📝 Enter ticket subject:",
    },
    "ticket_text": {
        "fa": "📝 متن پیام خود را وارد کنید:",
        "en": "📝 Enter your message:",
    },
    "ticket_created": {
        "fa": "✅ تیکت شما ثبت شد.\n\nشماره تیکت: #{id}\nبه زودی پاسخ داده می‌شود.",
        "en": "✅ Ticket created.\n\nTicket ID: #{id}\nYou will receive a response soon.",
    },

    # ── Settings ──
    "settings_title": {
        "fa": "⚙️ تنظیمات",
        "en": "⚙️ Settings",
    },
    "settings_lang": {
        "fa": "🌐 زبان فعلی: {lang}\n\nزبان جدید را انتخاب کنید:",
        "en": "🌐 Current language: {lang}\n\nSelect new language:",
    },
    "lang_changed": {
        "fa": "✅ زبان به فارسی تغییر کرد.",
        "en": "✅ Language changed to English.",
    },

    # ── Common ──
    "back": {
        "fa": "◀️ بازگشت",
        "en": "◀️ Back",
    },
    "main_menu_btn": {
        "fa": "🏠 منوی اصلی",
        "en": "🏠 Main Menu",
    },
    "wallet_btn": {
        "fa": "💰 کیف پول",
        "en": "💰 Wallet",
    },
    "deposit_btn": {
        "fa": "💳 افزایش موجودی",
        "en": "💳 Deposit",
    },
    "transactions_btn": {
        "fa": "📊 تراکنش‌ها",
        "en": "📊 Transactions",
    },
    "new_order_btn": {
        "fa": "🛒 سفارش جدید",
        "en": "🛒 New Order",
    },
    "my_orders_btn": {
        "fa": "📋 سفارشات من",
        "en": "📋 My Orders",
    },
    "referral_btn": {
        "fa": "🎁 دعوت دوستان",
        "en": "🎁 Referral",
    },
    "support_btn": {
        "fa": "🎫 پشتیبانی",
        "en": "🎫 Support",
    },
    "settings_btn": {
        "fa": "⚙️ تنظیمات",
        "en": "⚙️ Settings",
    },
    "admin_btn": {
        "fa": "👑 پنل مدیریت",
        "en": "👑 Admin Panel",
    },
    "approve_btn": {
        "fa": "✅ تأیید",
        "en": "✅ Approve",
    },
    "reject_btn": {
        "fa": "❌ رد",
        "en": "❌ Reject",
    },
    "invalid_number": {
        "fa": "⚠️ لطفاً یک عدد معتبر وارد کنید.",
        "en": "⚠️ Please enter a valid number.",
    },
    "not_admin": {
        "fa": "⛔️ شما دسترسی ادمین ندارید.",
        "en": "⛔️ You don't have admin access.",
    },
}


def get_text(lang: str, key: str, **kwargs) -> str:
    """Get translated text with optional format args."""
    entry = TRANSLATIONS.get(key, {})
    text = entry.get(lang, entry.get("en", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
