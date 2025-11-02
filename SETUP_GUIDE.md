# 🚀 Quick Setup Guide - Google Sheets Integration

## Bước 1: Cài đặt thư viện (5 phút)

```powershell
pip install -r requirements.txt
```

## Bước 2: Setup Google Cloud (10 phút)

### 2.1. Tạo Project & Enable APIs
1. Vào https://console.cloud.google.com/
2. Tạo project mới: **Work Report System**
3. Enable APIs:
   - Google Sheets API: https://console.cloud.google.com/apis/library/sheets.googleapis.com
   - Google Drive API: https://console.cloud.google.com/apis/library/drive.googleapis.com

### 2.2. Tạo Service Account
1. Vào: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click **+ CREATE SERVICE ACCOUNT**
3. Nhập:
   - **Service account name**: `work-report-bot`
   - **Service account ID**: tự động tạo
4. Click **CREATE AND CONTINUE**
5. Bỏ qua phần Grant access → Click **DONE**

### 2.3. Download Credentials JSON
1. Click vào service account vừa tạo
2. Tab **KEYS** → **ADD KEY** → **Create new key**
3. Chọn **JSON** → **CREATE**
4. File sẽ download về (tên dạng: `project-xxx-xxxx.json`)
5. **Đổi tên thành `credentials.json`**
6. **Copy vào thư mục project**

```powershell
# Đổi tên file
Rename-Item "project-xxx-xxxx.json" "credentials.json"

# Copy vào project
Move-Item "credentials.json" "c:\Users\Bao\Desktop\Work\App\report_task\"
```

## Bước 3: Setup Google Sheets (5 phút)

### 3.1. Tạo Spreadsheet
1. Vào Google Sheets: https://sheets.google.com
2. Tạo spreadsheet mới
3. Đặt tên: **Work Report Database**

### 3.2. Share với Service Account
1. Mở file `credentials.json`
2. Tìm dòng `"client_email"`, copy email (dạng: xxx@xxx.iam.gserviceaccount.com)
   
   ```json
   {
     "client_email": "work-report-bot@project-123.iam.gserviceaccount.com"
   }
   ```

3. Trong Google Sheets, click **Share** (góc phải trên)
4. Paste email Service Account
5. Chọn quyền: **Editor**
6. **Bỏ tick** "Notify people"
7. Click **Share**

### 3.3. Lấy Spreadsheet ID
1. Xem URL của spreadsheet:
   ```
   https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit
   ```
2. Copy phần ID: `1a2b3c4d5e6f7g8h9i0j`

## Bước 4: Cấu hình .env (2 phút)

```powershell
# Copy template
copy .env.example .env

# Edit file
notepad .env
```

Điền vào file `.env`:
```env
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=1a2b3c4d5e6f7g8h9i0j
GOOGLE_SHEETS_SPREADSHEET_NAME=Work Report Database
```

**Lưu file và đóng**

## Bước 5: Test kết nối (1 phút)

Tạo file `test_connection.py`:

```python
from database.connection import test_connection

if test_connection():
    print("✅ Kết nối thành công!")
else:
    print("❌ Kết nối thất bại. Kiểm tra lại:")
    print("  1. File credentials.json có đúng không?")
    print("  2. Đã share spreadsheet chưa?")
    print("  3. Spreadsheet ID đúng chưa?")
```

Chạy:
```powershell
python test_connection.py
```

## Bước 6: Import báo cáo đầu tiên (2 phút)

```python
from database.connection import connect_google_sheets
from main import import_single_report

# Kết nối
client, spreadsheet = connect_google_sheets()

# Thông tin nhân viên
employee = {
    "employeeCode": "NV001",
    "fullName": "Nguyễn Văn A",
    "email": "a.nguyen@company.com",
    "departmentCode": "IT",
    "departmentName": "Phòng CNTT",
    "position": "Developer",
    "managerCode": ""
}

# Import
excel_path = "./input/202509_Bao cao cong viec_thinhdv.xlsx"
sheet_name = "Th8-T9"
import_single_report(spreadsheet, excel_path, employee)

print("\\n✅ Hoàn tất! Kiểm tra Google Sheets để xem dữ liệu.")
```

## ✅ Checklist

- [ ] Đã cài `pip install -r requirements.txt`
- [ ] Đã tạo Google Cloud Project
- [ ] Đã enable Google Sheets API & Drive API
- [ ] Đã tạo Service Account
- [ ] Đã download `credentials.json` và đặt vào thư mục project
- [ ] Đã tạo Google Spreadsheet
- [ ] Đã share spreadsheet với email Service Account (quyền Editor)
- [ ] Đã copy Spreadsheet ID
- [ ] Đã tạo file `.env` với đầy đủ thông tin
- [ ] Test kết nối thành công
- [ ] Import báo cáo đầu tiên thành công

## 🎉 Hoàn thành!

Hệ thống đã sẵn sàng. Google Sheets của bạn sẽ tự động có các sheet:
- ✅ Employees
- ✅ Work_Reports
- ✅ Tasks_Actual
- ✅ Tasks_Planned
- ✅ Reviews

Bây giờ bạn có thể:
1. Import thêm báo cáo
2. Tạo dashboard trong Google Data Studio
3. Sử dụng QUERY functions để phân tích
4. Export sang BI tools

## 🆘 Gặp lỗi?

### Lỗi phổ biến:

**1. "Import could not be resolved"**
```powershell
pip install gspread gspread-dataframe oauth2client google-auth
```

**2. "The caller does not have permission"**
- Kiểm tra đã share spreadsheet với Service Account chưa
- Đảm bảo quyền là **Editor**, không phải Viewer

**3. "Unable to parse range"**
- Để hệ thống tự tạo sheets lần đầu chạy
- Hoặc tạo thủ công các sheet với đúng tên

**4. "credentials.json not found"**
- Kiểm tra file có trong thư mục project
- Kiểm tra tên file chính xác: `credentials.json`

---

**Thời gian setup tổng cộng: ~25 phút**
