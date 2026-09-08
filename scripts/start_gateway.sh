#!/usr/bin/env bash
# =============================================================================
# Kịch bản khởi chạy đồng thời Nginx Gateway và Cloudflare Tunnel
# =============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

if [ ! -f .env ]; then
    echo "[!] Không tìm thấy file .env. Đang sao chép từ .env.example..."
    cp .env.example .env
    echo "[!] Vui lòng cập nhật CLOUDFLARE_TUNNEL_TOKEN trong .env trước khi chạy!"
    exit 1
fi

echo "[+] Khởi động cụm Docker Edge Gateway & Cloudflare Tunnel..."
docker compose -f docker/docker-compose.infra.yml up -d --build

echo "[✓] Edge Gateway đã sẵn sàng tại cổng 80!"
docker compose -f docker/docker-compose.infra.yml ps
