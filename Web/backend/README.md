# Hệ thống Phạt Nguội - Backend API

FastAPI backend cho hệ thống quản lý phạt nguội giao thông.

## Cài đặt

1. Tạo virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
\`\`\`

2. Cài đặt dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Cấu hình database:
- Tạo PostgreSQL database
- Cập nhật DATABASE_URL trong file `.env`

4. Chạy migrations:
\`\`\`bash
python scripts/create_database.py
\`\`\`

5. Seed dữ liệu mẫu:
\`\`\`bash
python scripts/seed_data.py
\`\`\`

6. Chạy server:
\`\`\`bash
python main.py
\`\`\`

API sẽ chạy tại: http://localhost:8000
API Documentation: http://localhost:8000/docs

## Tài khoản mặc định

- **Authority**: admin / admin123
- **Officer 1**: officer1 / officer123  
- **Officer 2**: officer2 / officer123
- **Citizen**: citizen1 / citizen123

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Đăng nhập
- `GET /api/v1/auth/me` - Thông tin user hiện tại

### Violations
- `GET /api/v1/violations/` - Danh sách vi phạm
- `GET /api/v1/violations/lookup` - Tra cứu vi phạm (public)
- `POST /api/v1/violations/report` - Báo cáo vi phạm
- `PUT /api/v1/violations/{id}` - Cập nhật vi phạm

### Cameras
- `GET /api/v1/cameras/` - Danh sách camera
- `POST /api/v1/cameras/` - Tạo camera mới
- `PUT /api/v1/cameras/{id}` - Cập nhật camera

### Officer
- `GET /api/v1/officer/assigned-violations` - Vi phạm được giao
- `PUT /api/v1/officer/process-violation/{id}` - Xử lý vi phạm
- `POST /api/v1/officer/quick-process` - Xử lý hàng loạt

### Citizen
- `GET /api/v1/citizen/my-violations` - Vi phạm đã báo cáo
- `POST /api/v1/citizen/report-violation` - Báo cáo vi phạm
- `PUT /api/v1/citizen/update-profile` - Cập nhật hồ sơ

### Statistics & Reports
- `GET /api/v1/statistics/dashboard` - Thống kê tổng quan
- `GET /api/v1/reports/violation-trends` - Xu hướng vi phạm
- `GET /api/v1/reports/performance-report` - Báo cáo hiệu suất

## Cấu trúc thư mục

\`\`\`
backend/
├── app/
│   ├── api/v1/endpoints/    # API endpoints
│   ├── core/               # Cấu hình, security
│   ├── crud/               # Database operations
│   ├── db/                 # Database setup
│   ├── models/             # SQLAlchemy models
│   └── schemas/            # Pydantic schemas
├── alembic/                # Database migrations
├── scripts/                # Utility scripts
├── uploads/                # File uploads
└── main.py                 # FastAPI app
