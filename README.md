# Mini Project Intern

## Giới thiệu
Dự án thực tập sinh (Intern).

## Tech Stack
- Python, Flask
- MySQL
- Docker

## Yêu cầu
- Docker & Docker Compose

## Cài đặt & Chạy

### 1. Clone project
```bash
git clone <repository_url>
cd mini-project-intern
```

### 2. Tạo file .env.docker
Sao chép file `.env.example` thành `.env.docker`:
```bash
cp backend/.env.example backend/.env.docker
```
*Lưu ý: Mở file `backend/.env.docker` và chỉnh sửa các biến kết nối (đặc biệt là đổi `DB_HOST=db`) và thêm các biến cấu hình cho container MySQL.*

### 3. Chạy
```bash
docker compose up --build -d
```

### 4. Kiểm tra
Truy cập ứng dụng tại: [http://localhost:5000](http://localhost:5000)

## Cấu trúc project
```text
mini-project-intern/
├── backend/
│   ├── app/
│   ├── migrations/
│   ├── Dockerfile
│   └── .env.docker
└── docker-compose.yml
```

## API Endpoints
| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET    | /        | Hello World |

## Biến môi trường
| Biến | Mô tả | Ví dụ |
|------|-------|-------|
| DB_HOST | Host kết nối database (`db` cho Docker, `localhost` cho local) | db |
| DB_PORT | Port database | 3306 |
| DB_USER | Username kết nối database | root |
| DB_PASSWORD | Mật khẩu kết nối database | 123456 |
| DB_NAME | Tên database kết nối | intern_project |
| MYSQL_ROOT_PASSWORD | Mật khẩu root của container MySQL (cần khớp với `DB_PASSWORD`) | 123456 |
| MYSQL_DATABASE | Tên database khởi tạo trong container MySQL (cần khớp với `DB_NAME`) | intern_project |
| DEBUG | Chế độ debug của ứng dụng | True |
