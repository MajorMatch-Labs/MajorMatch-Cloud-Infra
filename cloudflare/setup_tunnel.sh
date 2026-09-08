#!/usr/bin/env bash
# =============================================================================
# Kịch bản tự động cài đặt và xác thực Cloudflare Tunnel trên Edge Gateway
# =============================================================================
set -e

echo "[+] Bắt đầu kiểm tra và cài đặt cloudflared..."
if ! command -v cloudflared &> /dev/null; then
    curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared.deb
    rm -f cloudflared.deb
    echo "[+] Đã cài đặt cloudflared thành công!"
fi

echo "[+] Đăng nhập Cloudflare Tunnel (Mở liên kết xác thực trên trình duyệt):"
cloudflared tunnel login

echo "[+] Khởi tạo Tunnel mới 'majormatch-edge':"
cloudflared tunnel create majormatch-edge

echo "[+] Tạo tệp định tuyến DNS cho api.majormatch.vn:"
cloudflared tunnel route dns majormatch-edge api.majormatch.vn

echo "[✓] Thiết lập hoàn tất! Hãy copy TUNNEL_TOKEN vào file .env để kích hoạt Docker."
