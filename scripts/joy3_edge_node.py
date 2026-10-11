#!/usr/bin/env python3
"""
MajorMatch - Joy 3 Edge Gateway Dispatcher
==========================================
Chạy trên Joy 3 (Termux / Minimal Ubuntu).
Đóng vai trò CỔNG BIÊN ĐIỀU PHỐI TRUNG TÂM (Central Edge Gateway):
- Đứng ở giữa đón 100% request từ Client (Trình duyệt Web).
- Hiển thị LOG THỜI GIAN THỰC (Real-time Console) cho mọi request đi qua Joy 3.
- Phân luồng:
    + CSDL / Hồ sơ / Tiến độ  ==> Gửi sang [AWS CLOUD DB] (Port 8001)
    + AI / LLM / RAG / GPU   ==> Gửi sang [HPC LEGION GPU] (Port 8000)
"""

import http.server
import json
import os
import signal
import socketserver
import subprocess
import sys
import time
import urllib.request
import urllib.error

# Cấu hình địa chỉ
AWS_SSH_TARGET = "ubuntu@13.250.26.54"
AWS_CLOUD_DB = "http://127.0.0.1:8001"
HPC_HOST_TAILSCALE = "http://100.123.107.114:8000"
HPC_HOST_WIFI = "http://192.168.100.155:8000"
EDGE_LISTEN_PORT = 8080

def get_hpc_host():
    """Tự động kiểm tra nốt HPC Legion khả dụng."""
    for host in [HPC_HOST_TAILSCALE, HPC_HOST_WIFI]:
        try:
            req = urllib.request.Request(f"{host}/docs", method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    return host
        except Exception:
            pass
    return HPC_HOST_TAILSCALE

ACTIVE_HPC = get_hpc_host()


class Joy3EdgeDispatcherHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        # Tắt log mặc định để format log tùy chỉnh đẹp mắt
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_GET(self):
        self.route_and_dispatch()

    def do_POST(self):
        self.route_and_dispatch()

    def route_and_dispatch(self):
        start_time = time.time()
        method = self.command
        path = self.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else None

        # 1. Phân loại tác vụ
        is_gpu = any(p in path for p in ["/roadmap/generate", "/chat/stream", "/assessment/calculate-match", "/upload-transcript"])
        
        if is_gpu:
            dest_tier = "⚡ [HPC GPU LEGION]"
            dest_color = "\033[92m"
            backend_url = f"{ACTIVE_HPC}{path}"
            desc = "Suy luận LLM (Qwen 2.5) & Tính toán Ma trận Cosine"
        else:
            dest_tier = "☁️  [AWS CLOUD DB]"
            dest_color = "\033[93m"
            backend_url = f"{AWS_CLOUD_DB}{path}"
            desc = "Truy vấn / Lưu trữ CSDL SQLite Bền vững trên AWS EC2"

        # Bóc tách thông tin sinh viên nếu có
        info_extra = ""
        if body and "application/json" in self.headers.get("Content-Type", ""):
            try:
                payload = json.loads(body.decode("utf-8", errors="ignore"))
                sid = payload.get("student_id", payload.get("id"))
                maj = payload.get("target_major", payload.get("target_major_id"))
                if sid or maj:
                    info_extra = f" | MSSV: \033[1m{sid or 'N/A'}\033[0m | Ngành: \033[1m{maj or 'N/A'}\033[0m"
            except Exception:
                pass

        # In log trực quan tại Joy 3 Terminal
        now_time = time.strftime("%H:%M:%S")
        print("\n\033[96m" + "─" * 72 + "\033[0m")
        print(f"📱 \033[1;96m[JOY 3 EDGE NODE - {now_time}]\033[0m")
        print(f"   ▶ Yêu cầu từ Client   : \033[1m{method} {path}\033[0m{info_extra}")
        print(f"   ▶ Phân luồng điều phối: {dest_color}{dest_tier}\033[0m ({desc})")
        print(f"   ▶ Backend chuyển tiếp : \033[90m{backend_url}\033[0m")

        headers = {k: v for k, v in self.headers.items() if k.lower() not in ["host", "content-length"]}
        if body:
            headers["Content-Length"] = str(len(body))

        try:
            req = urllib.request.Request(backend_url, data=body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=120.0) as resp:
                status_code = resp.status
                self.send_response(status_code)
                for k, v in resp.getheaders():
                    if k.lower() not in ["transfer-encoding", "content-length"]:
                        self.send_header(k, v)
                self.end_headers()

                is_stream = "text/event-stream" in resp.getheader("Content-Type", "")
                if is_stream:
                    print("   ⚡ \033[96m[STREAMING TOKENS]\033[0m  : Đang truyền trực tiếp token SSE về Trình duyệt...")

                total_bytes = 0
                while True:
                    chunk = resp.read(1024)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    self.wfile.write(chunk)
                    self.wfile.flush()

                elapsed_ms = round((time.time() - start_time) * 1000, 1)
                st_color = "\033[92m" if status_code < 400 else "\033[91m"
                print(f"   ◀ Kết quả phản hồi   : {st_color}{status_code} OK\033[0m ({elapsed_ms} ms, {total_bytes} bytes)")
                print(f"   📤 \033[94m[HOÀN TẤT TRẢ CLIENT]\033[0m: Đã chuyển tiếp dữ liệu an toàn qua Edge.")
        except urllib.error.HTTPError as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 1)
            print(f"   ⚠️ \033[91m[BACKEND TRẢ LỖI]\033[0m   : HTTP {e.code} ({elapsed_ms} ms)")
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 1)
            print(f"   ❌ \033[91m[LỖI KẾT NỐI]\033[0m        : {e} ({elapsed_ms} ms)")
            err_data = json.dumps({"detail": f"Joy 3 Edge Gateway forwarding error: {str(e)}"}).encode()
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(err_data)


def main():
    print("\033[1;92m" + "═" * 72)
    print("  🚀 KHỞI ĐỘNG JOY 3 EDGE GATEWAY - ĐIỀU PHỐI TOÀN BỘ LOG REALTIME")
    print("═" * 72 + "\033[0m")
    print(f"▶ Cổng lắng nghe Ingress : \033[93m0.0.0.0:{EDGE_LISTEN_PORT}\033[0m")
    print(f"▶ Nốt Cloud Database    : \033[93m{AWS_CLOUD_DB}\033[0m (SQLite AWS EC2)")
    print(f"▶ Nốt HPC GPU Compute   : \033[92m{ACTIVE_HPC}\033[0m (Legion RTX 4060)")

    print(f"\n[+] Đang mở SSH 2-Way Tunnel kết nối AWS EC2...")
    # -R 8000: Nhận mọi request Client từ Nginx AWS EC2 đổ về Joy 3:8080
    # -L 8001: Mở cầu nối để Joy 3 gọi trực tiếp vào Cloud DB trên AWS EC2
    ssh_cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=15",
        "-o", "ExitOnForwardFailure=yes",
        "-N",
        "-R", f"8000:127.0.0.1:{EDGE_LISTEN_PORT}",
        "-L", "8001:127.0.0.1:8001",
        AWS_SSH_TARGET
    ]

    tunnel = subprocess.Popen(ssh_cmd)
    time.sleep(2)

    if tunnel.poll() is not None:
        print("\033[91m[-] Lỗi: Không thể mở SSH Tunnel tới AWS EC2. Kiểm tra kết nối mạng!\033[0m")
    else:
        print("\033[92m[✓] SSH 2-Way Tunnel thành công! 100% Request Client sẽ đi qua Joy 3.\033[0m")

    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("0.0.0.0", EDGE_LISTEN_PORT), Joy3EdgeDispatcherHandler) as httpd:
            print("\n\033[1;93m>>> JOY 3 EDGE ĐANG LẮNG NGHE TOÀN BỘ LƯU LƯỢNG. SẴN SÀNG IN LOG! <<<\033[0m\n")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Đang tắt Joy 3 Edge Gateway...")
        tunnel.terminate()
        tunnel.wait()
        print("[✓] Đã giải phóng tài nguyên.")


if __name__ == "__main__":
    main()
