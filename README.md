# 🛒 SMM Marketplace Bot

Professional Telegram bot for SMM services marketplace.

## Features

- 🌐 **Bilingual** — Persian (FA) & English (EN) with in-bot language selection
- 💰 **Wallet System** — Deposit, balance tracking, transaction history
- 🛒 **Order System** — Browse panels → categories → services → place orders
- 👑 **Admin Panel** — Stats, deposit approval, order management, user management, tickets
- 🎫 **Ticket System** — User support with admin replies
- 🎁 **Referral Program** — Invite friends, earn commission
- 📊 **Loyalty Levels** — Bronze → Silver → Gold → Diamond
- 💾 **Auto Backup** — Hourly database backups

## Quick Start

```bash
# 1. Clone
git clone https://github.com/moha100h/smm-marketplace.git
cd smm-marketplace

# 2. Install
chmod +x install.sh
./install.sh

# 3. Edit .env with your bot token and admin ID
nano .env

# 4. Restart
docker compose down && docker compose up -d --build

# 5. View logs
docker compose logs -f backend
```

## Tech Stack

- **Backend**: Python 3.12 + aiogram 3.x + SQLAlchemy 2.x
- **Database**: PostgreSQL 16
- **Cache**: Redis 7
- **Deployment**: Docker Compose

## Structure

```
backend/
├── app/
│   ├── core/          # Config, i18n
│   ├── db/            # Database setup
│   ├── models/        # SQLAlchemy models
│   ├── bot/
│   │   ├── handlers/  # Bot handlers
│   │   ├── keyboards/ # Inline keyboards
│   │   └── middlewares.py
│   └── services/      # Business logic
├── main.py
└── requirements.txt
```

## License

MIT
