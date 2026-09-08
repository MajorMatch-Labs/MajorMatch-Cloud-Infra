#!/usr/bin/env bash
# =============================================================================
# Giám sát kết nối mạng (Liveness Monitor) giữa Edge Gateway và HPC Node
# =============================================================================
HPC_HOST="${1:-127.0.0.1}"
HPC_PORT="${2:-8000}"
INTERVAL_SEC=15

echo "[+] Bắt đầu giám sát sức khỏe Private HPC Compute Node ($HPC_HOST:$HPC_PORT)..."

while true; do
    TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://${HPC_HOST}:${HPC_PORT}/api/v1/health" --max-time 3 || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        echo "[$TIMESTAMP] [OK] HPC Node trực tuyến (HTTP 200)."
    else
        echo "[$TIMESTAMP] [WARN] Cảnh báo: Không thể kết nối HPC Node! Mã lỗi: $HTTP_CODE"
    fi

    sleep "$INTERVAL_SEC"
done
