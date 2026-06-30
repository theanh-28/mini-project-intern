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
* `core/`: Cấu hình hệ thống (`config.py`).
* `db/`: Kết nối DB (`base.py`, `session.py`).
* `models/`: Khai báo SQLAlchemy Models.
* `repositories/`: Truy vấn CSDL.
* `routes/`: Định nghĩa các API Endpoints/Routes.
* `schemas/`: Pydantic Schemas (Request/Response).
* `services/`: Xử lý logic nghiệp vụ.

---

## 🧪 Kiểm thử (Testing)

Dự án được viết test toàn diện sử dụng **`pytest`**, **`pytest-mock`**, và **`freezegun`**.

### 1. Phân loại các bài test có sẵn
* **Unit Tests (Kiểm thử đơn vị):**
  * `tests/unit/test_security.py`: Kiểm thử các hàm bảo mật (băm mật khẩu, kiểm tra mật khẩu, mã hóa và giải mã JWT token).
  * `tests/unit/test_user_service.py`: Kiểm thử logic nghiệp vụ xác thực người dùng trong `UserService` sử dụng mock repository (Factory Fixture).
  * `tests/unit/test_user_repository.py`: Kiểm thử các câu lệnh truy vấn của `UserRepository` trực tiếp trên database **SQLite In-Memory** để đảm bảo độc lập và tốc độ cực nhanh.
* **Integration Tests (Kiểm thử tích hợp):**
  * `tests/integration/test_auth_routes.py`: Kiểm thử tích hợp toàn bộ luồng đăng nhập của API `/auth/login` (POST) bằng Flask Test Client (mã trạng thái 200, 400, 401, 403) và SQLite test database.

### 2. Hướng dẫn chạy test
Tại thư mục `/backend` chạy:

```bash
# Chạy toàn bộ các bài test
uv run pytest

# Chạy test hiển thị log chi tiết
uv run pytest -v -s

# Chỉ chạy các unit test
uv run pytest tests/unit/
```
