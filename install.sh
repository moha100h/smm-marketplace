#!/bin/bash
set -e

echo "========================================"
echo "   🚀  SMM Marketplace — Installation"
echo "========================================"
echo ""

# ── Check Docker ──────────────────────────────────────────────────────────────
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker installed."
else
    echo "✅ Docker already installed."
fi

if ! command -v docker compose &> /dev/null; then
    echo "📦 Installing Docker Compose plugin..."
    apt-get update && apt-get install -y docker-compose-plugin
    echo "✅ Docker Compose installed."
else
    echo "✅ Docker Compose already installed."
fi
echo ""

# ── Get Bot Token & Admin ID ──────────────────────────────────────────────────
read -p "🤖 Telegram Bot Token (from @BotFather): " BOT_TOKEN
read -p "👑 Admin Numeric ID (from @userinfobot): " ADMIN_IDS

# ── Create .env ───────────────────────────────────────────────────────────────
JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")

cat > .env <<EOF
BOT_TOKEN=$BOT_TOKEN
ADMIN_IDS=$ADMIN_IDS
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/sessionbot
REDIS_URL=redis://redis:6379/0
JWT_SECRET=$JWT_SECRET
JWT_EXPIRE_HOURS=24
JWT_REFRESH_EXPIRE_DAYS=7
USDT_TRC20_ADDRESS=
USDT_BEP20_ADDRESS=
BTC_ADDRESS=
ETH_ADDRESS=
LTC_ADDRESS=
REFERRAL_COMMISSION_PERCENT=10
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=false
APP_DOMAIN=localhost
BACKUP_INTERVAL_HOURS=1
BACKUP_RETAIN_DAYS=7
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

echo ""
echo "✅ .env created with secure JWT secret."

# ── Create directories ────────────────────────────────────────────────────────
mkdir -p data logs backups ssl

# ── Build & Start ─────────────────────────────────────────────────────────────
echo ""
echo "🔨 Building Docker images..."
docker compose up -d --build

echo ""
echo "⏳ Waiting for database to be ready..."
sleep 10

echo ""
echo "========================================"
echo "   ✅ SMM Marketplace is running!"
echo "========================================"
echo ""
echo "📋 Backend API:    http://localhost:8000"
echo "📋 Frontend:       http://localhost:3000"
echo "📋 API Docs:       http://localhost:8000/docs"
echo "📋 Bot Token:      ${BOT_TOKEN:0:10}..."
echo ""
echo "📋 مشاهده لاگ‌ها:    docker compose logs -f"
echo "🔄 ریستارت:          docker compose restart"
echo "🛑 توقف:             docker compose down"
echo ""
echo "🔗 لینک بات: https://t.me/$(echo $BOT_TOKEN | cut -d: -f1)"
echo ""
