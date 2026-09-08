# MajorMatch Cloud & Edge Gateway Infrastructure

Kho lưu trữ cấu hình hạ tầng mạng phân tán, cổng biên điều phối và kết nối bảo mật **Zero-Trust** của hệ thống **MajorMatch**.

* **Repository chính thức:** [https://github.com/MajorMatch-Labs/MajorMatch-Cloud-Infra](https://github.com/MajorMatch-Labs/MajorMatch-Cloud-Infra)
* **Tổ chức phát triển:** MajorMatch-Labs
* **Môn học ứng dụng:** Điện toán đám mây (Cloud Computing) & Đồ án tốt nghiệp

---

## 1. Kiến trúc Hạ tầng (Infrastructure Architecture)

1. **Zero-Trust Network Access (Cloudflare Tunnel):**
   * Kết nối cổng biên ra mạng Internet thông qua đường hầm mã hóa hai chiều.
   * **Tuyệt đối không mở port Router (No NAT/Port Forwarding)**, miễn nhiễm trước các đợt quét cổng tự động trên Internet.
2. **Cổng biên Nginx Reverse Proxy (Edge Gateway):**
   * **Token Bucket Rate Limiting:** Giới hạn tối đa 10 requests/phút cho các API tính toán AI nặng (`/api/v1/roadmap/generate`, `/api/v1/analysis/skill-gap`) chống quá tải VRAM GPU.
   * **Bảo mật OWASP:** Tích hợp bộ Header bảo vệ toàn diện (HSTS, CSP, X-Frame-Options, X-Content-Type-Options).
   * **Hỗ trợ SSE Streaming:** Cấu hình tắt đệm (`proxy_buffering off`) phục vụ phản hồi mượt mà cho Trợ lý ảo Qwen 2.5.
3. **Bộ đệm SQLite Response Cache:**
   * Lưu trữ cục bộ các kết quả phân tích mẫu và khung chương trình chuẩn, phản hồi tức thì với độ trễ $< 5\text{ms}$.

---

## 2. Hướng dẫn Khởi chạy Nhanh (Quick Start)

### 1. Chuẩn bị cấu hình:
```bash
cp .env.example .env
# Chỉnh sửa token Cloudflare Tunnel trong .env
nano .env
```

### 2. Khởi chạy cụm Docker Compose:
```bash
bash scripts/start_gateway.sh
```

### 3. Kiểm tra trạng thái vận hành:
```bash
docker compose -f docker/docker-compose.infra.yml ps
curl http://localhost/healthz
```
