# 🚀 SMM Marketplace — Enterprise Telegram Virtual Services Platform

Complete, production-ready SMM panel platform with Telegram bot, FastAPI backend, and Next.js frontend.

---

## ✨ Features

### 👤 User Panel
- 🌐 Bilingual (Persian/English) with permanent language storage
- 📦 Hierarchical marketplace: Panel → Category → Subcategory → Service
- 📝 Dynamic order forms (text, number, URL, select, checkbox, file, multi-select, textarea)
- 💰 Complete wallet system with transaction history
- 💳 Crypto payments (USDT TRC20/BEP20, BTC, ETH, LTC)
- 📋 Order tracking with 9 statuses
- 🎟 Discount & coupon system
- 🎁 Referral program with commission tracking
- 🏆 Loyalty program (Bronze → Silver → Gold → Platinum → Diamond)
- 🎫 Support ticket system with file attachments
- 🔔 Real-time notifications

### ⚙️ Admin Panel
- 📊 Order management (accept, reject, complete, partial complete, refund)
- 🔧 Service management (CRUD for panels, categories, services)
- 🌐 Multi-provider SMM API system with unlimited providers
- 🔄 Auto service import & synchronization
- 🎯 Smart routing engine (cheapest, fastest, highest success rate)
- 🛡 Failover system — automatic provider switching
- 📈 Health monitoring (response time, availability, success rate)
- 💱 Auto pricing engine (fixed, percentage, dynamic)
- 💳 Payment verification & wallet management
- 👥 User management
- 📊 Advanced analytics & reports
- 🔐 2FA for admins, audit logs, IP tracking

### 🏗 Architecture
- Clean Architecture with Repository Pattern
- Service Layer + Dependency Injection
- Event Driven Design
- Async Programming throughout
- Modular structure

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, Aiogram 3.x, FastAPI, SQLAlchemy 2.x |
| Database | PostgreSQL 16, Redis 7 |
| Frontend | React, Next.js, TypeScript, TailwindCSS, Shadcn UI |
| Infrastructure | Docker, Docker Compose, Nginx, SSL |
| Auth | JWT, Refresh Tokens, bcrypt |
| Scheduler | APScheduler |

---

## 🚀 Quick Install

### One-Command Install
```bash
git clone https://github.com/moha100h/smm-marketplace.git
cd smm-marketplace
chmod +x install.sh
./install.sh
```

The installer asks ONLY:
1. Telegram Bot Token
2. Admin Numeric ID

Then automatically:
- Installs Docker & Docker Compose
- Configures PostgreSQL & Redis
- Creates database & runs migrations
- Builds frontend & backend
- Configures Nginx & SSL
- Starts all services

---

## 📋 Manual Setup

```bash
# 1. Clone
git clone https://github.com/moha100h/smm-marketplace.git
cd smm-marketplace

# 2. Configure
cp .env.example .env
# Edit .env with your values

# 3. Start
docker compose up -d --build

# 4. Run migrations
docker compose exec backend alembic upgrade head
```

---

## 📁 Project Structure

```
smm-marketplace/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, security
│   │   ├── db/            # Database setup
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── repositories/  # Repository pattern
│   │   ├── services/      # Business logic
│   │   ├── adapters/      # SMM provider adapters
│   │   ├── api/v1/        # FastAPI endpoints
│   │   ├── bot/           # Telegram bot
│   │   │   ├── handlers/  # Bot handlers
│   │   │   ├── keyboards/ # Inline & reply keyboards
│   │   │   └── middlewares/
│   │   ├── tasks/         # Background tasks
│   │   └── utils/         # Utilities
│   ├── alembic/           # Database migrations
│   ├── main.py            # Entry point
│   └── requirements.txt
├── frontend/              # Next.js frontend
├── docker-compose.yml
├── Dockerfile.frontend
├── nginx.conf
├── install.sh
└── README.md
```

---

## 🔐 Security

- JWT Authentication with refresh tokens
- Rate limiting (API & bot)
- SQL injection protection (SQLAlchemy)
- XSS & CSRF protection
- Secure headers (Nginx)
- IP tracking & audit logs
- Password hashing (bcrypt)
- Environment variables for secrets
- 2FA ready for admins

---

## 📊 Database

Complete PostgreSQL schema with:
- Foreign keys & constraints
- Indexes for performance
- Alembic migrations
- Automatic backup system

---

## 🔄 Order Lifecycle

```
User → Select Service → Fill Form → Calculate Cost → Pay → Create Order
                                                    ↓
                    Pending → Awaiting Review → Accepted → Processing
                                                    ↓
            Partially Completed → Completed / Rejected / Cancelled / Refunded
```

### Partial Completion Engine
If provider delivers less than ordered:
- Calculate remaining quantity
- Calculate refund amount
- Credit wallet automatically
- Notify user
- Create transaction record

---

## 🌐 SMM Provider System

Support unlimited providers with:
- Universal adapter layer
- Auto service import
- Smart routing (cheapest/fastest/best)
- Automatic failover
- Health monitoring

---

## 📝 License

MIT License — Free for commercial use
