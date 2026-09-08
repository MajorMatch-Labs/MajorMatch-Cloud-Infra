#!/usr/bin/env bash
# =============================================================================
# Sao lưu cơ sở dữ liệu bộ đệm SQLite Cache
# =============================================================================
set -e

BACKUP_DIR="/var/backups/majormatch"
CACHE_DB="/var/cache/majormatch/response_cache.db"
DATE=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR"

if [ -f "$CACHE_DB" ]; then
    echo "[+] Đang sao lưu SQLite cache sang $BACKUP_DIR/cache_$DATE.db..."
    sqlite3 "$CACHE_DB" ".backup '$BACKUP_DIR/cache_$DATE.db'"
    echo "[✓] Sao lưu hoàn tất!"
    # Xóa bản backup cũ hơn 7 ngày
    find "$BACKUP_DIR" -type f -name "cache_*.db" -mtime +7 -delete
else
    echo "[!] Tệp CSDL cache chưa tồn tại, bỏ qua sao lưu."
fi
