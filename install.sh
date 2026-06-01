#!/bin/bash
set -e

echo "🚀 SMM Marketplace — Installation"
echo "=================================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose not found."
    exit 1
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your BOT_TOKEN and ADMIN_IDS before running!"
    echo ""
    read -p "Press Enter after editing .env..."
fi

# Build and start
echo "🔨 Building containers..."
docker compose up -d --build

echo ""
echo "✅ Installation complete!"
echo "📋 View logs: docker compose logs -f backend"
echo "🛑 Stop: docker compose down"
