# 🐍 Flask Backend

Backend viết bằng Flask, kết nối MySQL dùng SQLAlchemy và quản lý migrations bằng Alembic. Sử dụng `uv` làm trình quản lý package.

## 🛠️ Công nghệ chính
* Python >= 3.13, Flask 3.1, SQLAlchemy 2.0, Alembic 1.18, Pydantic v2
* Quản lý gói bằng `uv`

---

## 💻 Cài đặt Local (Không qua Docker)

### 1. Cài đặt thư viện
Yêu cầu đã cài đặt Python 3.13 và `uv`. Tại thư mục `/backend` chạy:
```bash
uv sync
```

### 2. Cấu hình môi trường
Sao chép và cấu hình thông tin DB của bạn:
```bash
cp .env.example .env
```

### 3. Chạy Migration & Khởi động Server
```bash
# Chạy migration database
uv run alembic upgrade head

# Chạy server
uv run python -m app.main
# Hoặc: uv run flask --app app.main:app run --port 5000 --debug
```

---

## 📁 Phân lớp thư mục `app/`
* `api/`: API Endpoints/Routes.
* `core/`: Cấu hình hệ thống (`config.py`).
* `db/`: Kết nối DB (`base.py`).
* `models/`: Khai báo SQLAlchemy Models.
* `repositories/`: Truy vấn CSDL.
* `schemas/`: Pydantic Schemas (Request/Response).
* `services/`: Xử lý logic nghiệp vụ.
