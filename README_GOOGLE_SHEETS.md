# Work Report System - Google Sheets Integration

Hệ thống quản lý báo cáo công việc nhân viên với Google Sheets làm database.

## 📋 Tính năng

- ✅ Extract dữ liệu từ file Excel báo cáo công việc
- ✅ Lưu trữ dữ liệu vào Google Sheets (thay vì MongoDB)
- ✅ Quản lý thông tin nhân viên
- ✅ Theo dõi công việc thực hiện và kế hoạch
- ✅ Hỗ trợ task/subtask phân cấp không giới hạn
- ✅ Batch import nhiều báo cáo
- ✅ Dashboard-ready data structure

## 🏗️ Cấu trúc Google Sheets

Hệ thống sẽ tự động tạo các sheet sau trong Google Spreadsheet:

### 1. **Employees** - Thông tin nhân viên
| Cột | Mô tả |
|-----|-------|
| employeeCode | Mã nhân viên (unique) |
| fullName | Họ tên |
| email | Email |
| departmentCode | Mã phòng ban |
| departmentName | Tên phòng ban |
| position | Chức vụ |
| managerCode | Mã quản lý |
| createdAt | Ngày tạo |
| updatedAt | Ngày cập nhật |

### 2. **Work_Reports** - Báo cáo công việc
| Cột | Mô tả |
|-----|-------|
| reportCode | Mã báo cáo (unique) |
| employeeCode | Mã nhân viên |
| employeeName | Tên nhân viên |
| departmentCode | Mã phòng ban |
| reportPeriodYear | Năm báo cáo |
| reportPeriodMonth | Tháng báo cáo |
| reportPeriodStartDate | Ngày bắt đầu |
| reportPeriodEndDate | Ngày kết thúc |
| status | Trạng thái (draft/submitted/approved) |
| version | Phiên bản |
| createdAt | Ngày tạo |
| updatedAt | Ngày cập nhật |

### 3. **Tasks_Actual** - Công việc đã thực hiện
| Cột | Mô tả |
|-----|-------|
| taskId | ID task (unique) |
| reportCode | Mã báo cáo |
| stt | Số thứ tự (1, 1.1, 1.1.1, ...) |
| taskName | Tên công việc |
| taskType | Loại công việc |
| category | functional/project |
| startDate | Ngày bắt đầu |
| endDate | Ngày kết thúc |
| description | Mô tả yêu cầu |
| solution | Giải pháp thực hiện |
| evaluation | Đánh giá kết quả |
| level | Cấp độ (0, 1, 2, ...) |
| parentTaskId | ID task cha |
| hasSubtasks | Có subtask không |
| subtaskCount | Số lượng subtask |
| createdAt | Ngày tạo |

### 4. **Tasks_Planned** - Công việc kế hoạch
*Tương tự Tasks_Actual nhưng có thêm:*
| Cột | Mô tả |
|-----|-------|
| cost | Chi phí dự kiến |
| costUnit | Đơn vị (VND) |

### 5. **Reviews** - Đánh giá chung
| Cột | Mô tả |
|-----|-------|
| reportCode | Mã báo cáo |
| dailyWorkReview | Đánh giá công việc hằng ngày |
| professionalReview | Đánh giá thực hiện chuyên môn |
| createdAt | Ngày tạo |

## 🚀 Cài đặt

### 1. Cài đặt dependencies

```powershell
pip install -r requirements.txt
```

### 2. Cấu hình Google Sheets API

#### Bước 1: Tạo Google Cloud Project
1. Truy cập [Google Cloud Console](https://console.cloud.google.com/)
2. Tạo project mới hoặc chọn project hiện có
3. Enable **Google Sheets API** và **Google Drive API**

#### Bước 2: Tạo Service Account
1. Vào **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Nhập tên service account (vd: `work-report-bot`)
4. Click **Create and Continue**
5. Click **Done**

#### Bước 3: Tạo JSON Key
1. Click vào service account vừa tạo
2. Vào tab **Keys**
3. Click **Add Key** → **Create new key**
4. Chọn **JSON** và click **Create**
5. File JSON sẽ được download về máy
6. Đổi tên file thành `credentials.json`
7. Copy file vào thư mục project: `c:\Users\Bao\Desktop\Work\App\report_task\`

#### Bước 4: Tạo Google Spreadsheet
1. Tạo Google Spreadsheet mới hoặc sử dụng spreadsheet có sẵn
2. **QUAN TRỌNG**: Chia sẻ spreadsheet với email của Service Account
   - Mở file `credentials.json`
   - Copy email trong field `"client_email"` (dạng: `xxx@xxx.iam.gserviceaccount.com`)
   - Vào Google Sheets → Share → Dán email → Chọn quyền **Editor** → Send
3. Lấy Spreadsheet ID từ URL:
   - URL dạng: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
   - Copy phần `SPREADSHEET_ID`

### 3. Cấu hình môi trường

```powershell
# Copy file .env.example
copy .env.example .env

# Chỉnh sửa file .env
notepad .env
```

Nội dung file `.env`:
```env
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
GOOGLE_SHEETS_SPREADSHEET_NAME=Work Report Database
```

**Lưu ý**: Bạn có thể dùng `SPREADSHEET_ID` HOẶC `SPREADSHEET_NAME`, ưu tiên ID hơn.

## 📖 Sử dụng

### Import một báo cáo

```python
from database.connection import connect_google_sheets
from main import import_single_report

# Kết nối Google Sheets
client, spreadsheet = connect_google_sheets()

# Thông tin nhân viên
employee = {
    "employeeCode": "NV001",
    "fullName": "Nguyễn Văn A",
    "email": "a.nguyen@company.com",
    "departmentCode": "IT",
    "departmentName": "Phòng CNTT",
    "position": "Developer",
    "managerCode": "NV000"
}

# Import báo cáo
excel_path = "./input/baocao_NV001.xlsx"
import_single_report(spreadsheet, excel_path, employee)
```

### Import nhiều báo cáo

```python
from main import import_batch_reports

# Danh sách file Excel
excel_files = [
    "./input/baocao_NV001.xlsx",
    "./input/baocao_NV002.xlsx",
    "./input/baocao_NV003.xlsx"
]

# Danh sách nhân viên tương ứng
employees = [
    {"employeeCode": "NV001", "fullName": "Nguyễn Văn A", ...},
    {"employeeCode": "NV002", "fullName": "Trần Thị B", ...},
    {"employeeCode": "NV003", "fullName": "Lê Văn C", ...}
]

# Import batch
import_batch_reports(spreadsheet, excel_files, employees)
```

### Query dữ liệu

```python
from database.operations import (
    get_employee_by_code,
    get_reports_by_employee,
    get_reports_by_department
)

# Lấy thông tin nhân viên
employee = get_employee_by_code(spreadsheet, "NV001")

# Lấy báo cáo của nhân viên trong tháng 9/2025
reports = get_reports_by_employee(spreadsheet, "NV001", year=2025, month=9)

# Lấy tất cả báo cáo của phòng IT
dept_reports = get_reports_by_department(spreadsheet, "IT", year=2025)
```

## 🏗️ Cấu trúc thư mục

```
report_task/
├── config/
│   └── settings.py           # Cấu hình Google Sheets
├── database/
│   ├── connection.py         # Kết nối Google Sheets
│   └── operations.py         # CRUD operations
├── extractors/
│   ├── excel_reader.py       # Đọc file Excel
│   └── task_parser.py        # Parse tasks
├── utils/
│   ├── parsers.py            # Parse STT, date, period
│   ├── validators.py         # Validate data
│   └── features.py           # Helper functions
├── input/                    # Thư mục chứa file Excel input
├── main.py                   # Entry point
├── requirements.txt          # Python dependencies
├── credentials.json          # Google Service Account key (KHÔNG commit)
├── .env                      # Environment variables (KHÔNG commit)
├── .env.example              # Template .env
└── README.md                 # File này
```

## 🔒 Bảo mật

**QUAN TRỌNG**: Không commit các file sau:
- `credentials.json` - Chứa private key của Service Account
- `.env` - Chứa thông tin cấu hình nhạy cảm

Thêm vào `.gitignore`:
```
credentials.json
.env
*.json
!requirements.txt
```

## 📊 Dashboard & Analytics

Với dữ liệu trong Google Sheets, bạn có thể:

1. **Sử dụng Google Data Studio / Looker Studio**
   - Kết nối trực tiếp với Google Sheets
   - Tạo dashboard realtime
   - Visualization: charts, tables, pivot tables

2. **Sử dụng Google Sheets Functions**
   - QUERY(): SQL-like queries
   - FILTER(): Filter data
   - PIVOT(): Pivot tables
   - IMPORTRANGE(): Kết hợp nhiều sheets

3. **Export sang BI Tools**
   - Power BI
   - Tableau
   - Metabase

### Ví dụ Dashboard Queries

**Tổng số công việc theo phòng ban:**
```sql
=QUERY(Tasks_Actual!A:P, "SELECT E, COUNT(A) WHERE E IS NOT NULL GROUP BY E")
```

**Completion rate theo tháng:**
```sql
=QUERY(Work_Reports!A:L, "SELECT E, F, COUNT(A) WHERE G='completed' GROUP BY E, F")
```

## ⚡ Performance Tips

1. **Batch Operations**: Import nhiều báo cáo cùng lúc
2. **Caching**: Cache dữ liệu employee để tránh query lặp lại
3. **Rate Limiting**: Google Sheets API có giới hạn:
   - 100 requests/100 seconds/user
   - 500 requests/100 seconds/project
4. **Data Validation**: Validate trước khi insert để tránh rollback

## 🐛 Troubleshooting

### Lỗi: "The caller does not have permission"
- Kiểm tra đã share spreadsheet với email Service Account chưa
- Kiểm tra quyền Editor cho Service Account

### Lỗi: "Unable to parse range"
- Sheet names có thể bị sai
- Chạy lại để tự động tạo sheets

### Lỗi: "Import gspread could not be resolved"
- Chưa cài đặt dependencies: `pip install -r requirements.txt`

### Lỗi: "File credentials.json not found"
- Kiểm tra file credentials.json có trong thư mục project
- Kiểm tra đường dẫn trong file .env

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra logs để xác định lỗi
2. Verify Google Sheets API credentials
3. Kiểm tra permissions của spreadsheet

## 📝 License

MIT License - Tự do sử dụng cho mục đích cá nhân và thương mại.

---

**Lưu ý**: Đây là hệ thống chuyển từ MongoDB sang Google Sheets. Phù hợp với:
- Quy mô nhỏ - vừa (< 1000 nhân viên)
- Yêu cầu dashboard realtime
- Không có infrastructure để host database
- Muốn tích hợp với Google Workspace ecosystem
