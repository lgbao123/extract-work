# 📝 SUMMARY OF CHANGES: MongoDB → Google Sheets

## 🎯 Mục tiêu
Chuyển đổi hệ thống quản lý báo cáo công việc từ sử dụng **MongoDB** sang **Google Sheets** làm database.

## ✅ Các file đã thay đổi

### 1. **requirements.txt**
- ❌ Xóa: `pymongo==4.6.1`
- ✅ Thêm:
  - `gspread==5.12.0`
  - `gspread-dataframe==3.3.1`
  - `oauth2client==4.1.3`
  - `google-auth==2.23.4`
  - `google-auth-oauthlib==1.1.0`
  - `google-auth-httplib2==0.1.1`

### 2. **config/settings.py**
**Thay đổi:**
- ❌ Xóa MongoDB configuration:
  ```python
  MONGODB_URI = ...
  DATABASE_NAME = ...
  COLLECTION_EMPLOYEES = ...
  COLLECTION_WORK_REPORTS = ...
  ```
  
- ✅ Thêm Google Sheets configuration:
  ```python
  GOOGLE_SHEETS_CREDENTIALS_FILE = ...
  GOOGLE_SHEETS_SPREADSHEET_ID = ...
  GOOGLE_SHEETS_SPREADSHEET_NAME = ...
  SHEET_EMPLOYEES = "Employees"
  SHEET_WORK_REPORTS = "Work_Reports"
  SHEET_TASKS_ACTUAL = "Tasks_Actual"
  SHEET_TASKS_PLANNED = "Tasks_Planned"
  SHEET_REVIEWS = "Reviews"
  ```

### 3. **database/connection.py**
**Thay đổi hoàn toàn:**
- ❌ Xóa: `connect_mongodb()`, `close_mongodb()`, `test_connection()`
- ✅ Thêm:
  - `connect_google_sheets()` - Kết nối với Google Sheets API
  - `initialize_sheets()` - Tự động tạo các sheet cần thiết
  - `get_worksheet()` - Lấy worksheet theo tên
  - `test_connection()` - Test kết nối Google Sheets

**Tính năng mới:**
- Tự động tạo sheets với headers khi chưa tồn tại
- Format headers (màu xanh, chữ trắng, bold)
- Xác thực qua Service Account

### 4. **database/operations.py**
**Thay đổi tất cả functions:**

| Function | MongoDB Version | Google Sheets Version |
|----------|----------------|----------------------|
| `insert_employee()` | `db.insert_one()` | DataFrame append + `set_with_dataframe()` |
| `get_employee_by_code()` | `db.find_one()` | DataFrame query |
| `insert_work_report()` | `db.insert_one()` | Tách thành 3 sheets |
| `get_work_report_by_code()` | `db.find_one()` | DataFrame query |
| `get_reports_by_employee()` | `db.find()` | DataFrame filter |
| `get_reports_by_department()` | `db.find()` | DataFrame filter |

**Functions mới:**
- `_insert_tasks()` - Insert tasks vào Tasks_Actual/Tasks_Planned
- `_update_tasks()` - Update tasks (delete + insert)
- `_prepare_task_data()` - Chuẩn bị task data cho insert
- `_insert_reviews()` - Insert reviews
- `_update_reviews()` - Update reviews

**Thay đổi cấu trúc dữ liệu:**
- Từ nested documents (MongoDB) → Flat structure (Google Sheets)
- Work report được split thành multiple sheets
- Tasks được tách riêng với reportCode để join
- Reviews được tách riêng

### 5. **main.py**
**Thay đổi imports:**
```python
# Old
from database.connection import connect_mongodb, close_mongodb

# New
from database.connection import connect_google_sheets, get_worksheet
```

**Thay đổi functions:**
- `import_single_report()`: Thay `db` → `spreadsheet`
- `import_batch_reports()`: Thay `db` → `spreadsheet`
- `main()`: Thay `connect_mongodb()` → `connect_google_sheets()`

## 📄 Các file mới

### 1. **.env.example**
Template file cho environment variables:
```env
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
GOOGLE_SHEETS_SPREADSHEET_NAME=Work Report Database
```

### 2. **README_GOOGLE_SHEETS.md**
Documentation đầy đủ:
- Tính năng hệ thống
- Cấu trúc Google Sheets (5 sheets)
- Hướng dẫn cài đặt chi tiết
- Hướng dẫn sử dụng
- Dashboard & Analytics tips
- Troubleshooting

### 3. **SETUP_GUIDE.md**
Quick setup guide 6 bước:
1. Cài đặt thư viện
2. Setup Google Cloud
3. Setup Google Sheets
4. Cấu hình .env
5. Test kết nối
6. Import báo cáo đầu tiên

### 4. **test_connection.py**
Script test kết nối:
- Kiểm tra credentials.json
- Test Google Sheets connection
- Hiển thị thông tin spreadsheet
- Error handling với hướng dẫn khắc phục

### 5. **MIGRATION_GUIDE.md**
Hướng dẫn migration từ MongoDB:
- So sánh MongoDB vs Google Sheets
- Khi nào nên dùng cái nào
- Migration steps chi tiết
- Performance optimization
- Best practices

## 🏗️ Cấu trúc Google Sheets

Hệ thống tự động tạo 5 sheets:

### 1. **Employees** (9 columns)
```
employeeCode | fullName | email | departmentCode | departmentName | 
position | managerCode | createdAt | updatedAt
```

### 2. **Work_Reports** (12 columns)
```
reportCode | employeeCode | employeeName | departmentCode | 
reportPeriodYear | reportPeriodMonth | reportPeriodStartDate | 
reportPeriodEndDate | status | version | createdAt | updatedAt
```

### 3. **Tasks_Actual** (16 columns)
```
taskId | reportCode | stt | taskName | taskType | category | 
startDate | endDate | description | solution | evaluation | 
level | parentTaskId | hasSubtasks | subtaskCount | createdAt
```

### 4. **Tasks_Planned** (17 columns)
*Giống Tasks_Actual + cost & costUnit*

### 5. **Reviews** (4 columns)
```
reportCode | dailyWorkReview | professionalReview | createdAt
```

## 🔄 Thay đổi cách xử lý dữ liệu

### MongoDB (Nested)
```json
{
  "reportCode": "BC-2025-09-NV001",
  "employeeCode": "NV001",
  "actualWork": {
    "functionalTasks": [
      {"stt": "1", "taskName": "Task 1", ...}
    ],
    "projectTasks": [...]
  },
  "reviews": {
    "dailyWork": "...",
    "professional": "..."
  }
}
```

### Google Sheets (Flat + Normalized)

**Work_Reports:**
```
BC-2025-09-NV001 | NV001 | ... | 2025 | 9 | ...
```

**Tasks_Actual:**
```
task-001 | BC-2025-09-NV001 | 1 | Task 1 | ... | functional | ...
task-002 | BC-2025-09-NV001 | 1.1 | Subtask 1 | ... | functional | ...
```

**Reviews:**
```
BC-2025-09-NV001 | Daily work review text | Professional review text | ...
```

## 🚀 Cách sử dụng

### Setup (lần đầu)
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup Google Sheets (xem SETUP_GUIDE.md)
# - Tạo Service Account
# - Download credentials.json
# - Tạo spreadsheet và share

# 3. Config .env
copy .env.example .env
# Edit .env với credentials và spreadsheet ID

# 4. Test
python test_connection.py
```

### Import data
```python
from database.connection import connect_google_sheets
from main import import_single_report

client, spreadsheet = connect_google_sheets()

employee = {
    "employeeCode": "NV001",
    "fullName": "Nguyễn Văn A",
    ...
}

import_single_report(spreadsheet, "report.xlsx", employee)
```

## 📊 Ưu điểm của Google Sheets

✅ **Không cần infrastructure**
- Không cần setup MongoDB server
- Không cần hosting

✅ **Dashboard tích hợp sẵn**
- Google Data Studio / Looker Studio
- Real-time collaboration
- QUERY functions for SQL-like queries

✅ **Dễ dàng truy cập**
- Mọi người có thể xem/edit trực tiếp
- Không cần tool riêng

✅ **Backup tự động**
- Google tự động version history
- Export CSV/Excel bất cứ lúc nào

✅ **Chi phí thấp**
- Free (< 5M cells)
- Không cần pay for database hosting

## ⚠️ Hạn chế

❌ **Performance**
- Chậm với > 100K records
- API rate limit: 100 requests/100 seconds

❌ **Scalability**
- Tối đa 5M cells per spreadsheet
- Phù hợp < 1000 users

❌ **Query complexity**
- Không có aggregation pipeline
- Limited indexing

❌ **Transaction support**
- Không có ACID guarantees
- Eventual consistency

## 🎯 Khi nào nên dùng?

### ✅ Dùng Google Sheets khi:
- Quy mô nhỏ - vừa (< 1000 nhân viên)
- Cần dashboard nhanh
- Budget hạn chế
- Team đã dùng Google Workspace
- Cần collaboration real-time

### ❌ Dùng MongoDB khi:
- Quy mô lớn (> 1000 nhân viên)
- Cần performance cao
- Query phức tạp
- Yêu cầu bảo mật cao
- Production application quan trọng

## 📚 Tài liệu tham khảo

1. **README_GOOGLE_SHEETS.md** - Documentation đầy đủ
2. **SETUP_GUIDE.md** - Quick setup trong 25 phút
3. **MIGRATION_GUIDE.md** - Migration từ MongoDB
4. **test_connection.py** - Test script

## ✨ Next Steps

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Follow SETUP_GUIDE.md** để setup Google Sheets

3. **Run test:**
   ```powershell
   python test_connection.py
   ```

4. **Import data:**
   ```powershell
   python main.py
   ```

5. **Build dashboard** trong Google Data Studio

---

**Tổng kết:**
- ✅ Đã chuyển đổi hoàn toàn từ MongoDB → Google Sheets
- ✅ Maintain được tất cả functionality
- ✅ Thêm auto-initialization cho sheets
- ✅ Documentation đầy đủ
- ✅ Test script để verify
- ✅ Migration guide cho existing users

**Thời gian migration:** ~25 phút setup + data import time
