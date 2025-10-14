# 🔄 Migration Guide: MongoDB → Google Sheets

Hướng dẫn chuyển đổi từ hệ thống MongoDB sang Google Sheets.

## 📊 So sánh

| Aspect | MongoDB | Google Sheets |
|--------|---------|---------------|
| **Setup** | Cần MongoDB server | Chỉ cần Google account |
| **Infrastructure** | Database server | Cloud-based |
| **Cost** | Phí hosting DB | Free (< 5M cells) |
| **Scalability** | Cao (millions records) | Vừa (< 100K records) |
| **Query Speed** | Rất nhanh | Chậm với data lớn |
| **Dashboard** | Cần BI tool riêng | Google Data Studio built-in |
| **Collaboration** | Qua application | Real-time trong Sheets |
| **Backup** | Cần config | Google tự động |
| **API Rate Limit** | Không | 100 req/100s |

## 🎯 Khi nào nên dùng Google Sheets?

✅ **Phù hợp khi:**
- Quy mô nhỏ - vừa (< 1000 nhân viên)
- Cần dashboard nhanh, không cần setup phức tạp
- Team đã quen với Google Workspace
- Không có infrastructure để host database
- Cần collaboration real-time
- Budget hạn chế

❌ **KHÔNG phù hợp khi:**
- Quy mô lớn (> 1000 nhân viên)
- Cần query phức tạp, performance cao
- Dữ liệu nhạy cảm, yêu cầu bảo mật cao
- Cần transaction, ACID properties
- Integration phức tạp với nhiều hệ thống

## 🔧 Các thay đổi chính

### 1. Connection

**MongoDB:**
```python
from database.connection import connect_mongodb, close_mongodb

client, db = connect_mongodb()
# ... use db
close_mongodb(client)
```

**Google Sheets:**
```python
from database.connection import connect_google_sheets

client, spreadsheet = connect_google_sheets()
# ... use spreadsheet
# Không cần close (stateless)
```

### 2. Data Structure

**MongoDB Collections → Google Sheets Tabs**

| MongoDB Collection | Google Sheets Tab |
|-------------------|-------------------|
| employees | Employees |
| work_reports | Work_Reports |
| tasks (embedded) | Tasks_Actual, Tasks_Planned |
| reviews (embedded) | Reviews |

**MongoDB Embedded Documents → Separate Sheets**

MongoDB:
```json
{
  "reportCode": "BC-2025-09-NV001",
  "actualWork": {
    "functionalTasks": [...],
    "projectTasks": [...]
  }
}
```

Google Sheets:
- Work_Reports: Thông tin báo cáo
- Tasks_Actual: Các tasks (có reportCode để join)

### 3. Operations

**Insert:**

MongoDB:
```python
db.employees.insert_one(employee_data)
```

Google Sheets:
```python
insert_employee(spreadsheet, employee_data)
```

**Query:**

MongoDB:
```python
db.work_reports.find_one({"reportCode": code})
```

Google Sheets:
```python
get_work_report_by_code(spreadsheet, code)
```

**Update:**

MongoDB:
```python
db.work_reports.update_one(
    {"reportCode": code},
    {"$set": updates}
)
```

Google Sheets:
```python
# Delete old + Insert new (simpler approach)
insert_work_report(spreadsheet, updated_report, auto_update=True)
```

### 4. Queries & Aggregation

**MongoDB Aggregation Pipeline:**
```python
pipeline = [
    {"$match": {"departmentCode": "IT"}},
    {"$group": {
        "_id": "$reportPeriodMonth",
        "count": {"$sum": 1}
    }}
]
results = db.work_reports.aggregate(pipeline)
```

**Google Sheets (2 cách):**

*Cách 1: Python với pandas*
```python
from gspread_dataframe import get_as_dataframe

worksheet = spreadsheet.worksheet("Work_Reports")
df = get_as_dataframe(worksheet)
df = df[df['departmentCode'] == 'IT']
result = df.groupby('reportPeriodMonth')['reportCode'].count()
```

*Cách 2: QUERY trong Sheets*
```
=QUERY(Work_Reports!A:L, 
  "SELECT E, COUNT(A) 
   WHERE D='IT' 
   GROUP BY E", 1)
```

## 🚀 Migration Steps

### Bước 1: Backup MongoDB data

```python
# export_mongodb.py
from database.connection import connect_mongodb
import json

client, db = connect_mongodb()

# Export employees
employees = list(db.employees.find({}, {"_id": 0}))
with open("backup_employees.json", "w", encoding="utf-8") as f:
    json.dump(employees, f, ensure_ascii=False, indent=2, default=str)

# Export work_reports
reports = list(db.work_reports.find({}, {"_id": 0}))
with open("backup_reports.json", "w", encoding="utf-8") as f:
    json.dump(reports, f, ensure_ascii=False, indent=2, default=str)

print("✅ Backup completed!")
```

### Bước 2: Setup Google Sheets

Xem **SETUP_GUIDE.md** để setup Google Sheets.

### Bước 3: Import data từ backup

```python
# import_to_sheets.py
import json
from database.connection import connect_google_sheets
from database.operations import insert_employee, insert_work_report

client, spreadsheet = connect_google_sheets()

# Import employees
with open("backup_employees.json", "r", encoding="utf-8") as f:
    employees = json.load(f)
    
for emp in employees:
    insert_employee(spreadsheet, emp)
    print(f"✓ Imported: {emp['employeeCode']}")

# Import reports
with open("backup_reports.json", "r", encoding="utf-8") as f:
    reports = json.load(f)
    
for report in reports:
    insert_work_report(spreadsheet, report, auto_update=True)
    print(f"✓ Imported: {report['reportCode']}")

print("\\n✅ Migration completed!")
```

### Bước 4: Update application code

1. **Update imports:**
   ```python
   # Old
   from database.connection import connect_mongodb
   
   # New
   from database.connection import connect_google_sheets
   ```

2. **Update function calls:**
   ```python
   # Old
   client, db = connect_mongodb()
   insert_employee(db, employee_data)
   
   # New
   client, spreadsheet = connect_google_sheets()
   insert_employee(spreadsheet, employee_data)
   ```

3. **Update .env file:**
   ```env
   # Remove MongoDB config
   # MONGODB_URI=...
   # DATABASE_NAME=...
   
   # Add Google Sheets config
   GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json
   GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id
   GOOGLE_SHEETS_SPREADSHEET_NAME=Work Report Database
   ```

### Bước 5: Test

```python
python test_connection.py
```

### Bước 6: Verify data

1. Mở Google Sheets
2. Kiểm tra các tab: Employees, Work_Reports, Tasks_Actual, Tasks_Planned
3. Đếm số records so với MongoDB
4. Spot check một vài records

## 📈 Performance Optimization

### 1. Batch Operations
```python
# ❌ Slow: Insert từng record
for employee in employees:
    insert_employee(spreadsheet, employee)

# ✅ Fast: Batch insert với pandas
import pandas as pd
from gspread_dataframe import set_with_dataframe

df = pd.DataFrame(employees)
worksheet = spreadsheet.worksheet("Employees")
set_with_dataframe(worksheet, df)
```

### 2. Caching
```python
# Cache employee data để tránh query lặp lại
employee_cache = {}

def get_employee_cached(spreadsheet, code):
    if code not in employee_cache:
        employee_cache[code] = get_employee_by_code(spreadsheet, code)
    return employee_cache[code]
```

### 3. Rate Limiting
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    interval = 60.0 / calls_per_minute
    
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls_per_minute=50)
def insert_report_with_limit(spreadsheet, report):
    return insert_work_report(spreadsheet, report)
```

## 🎯 Best Practices

1. **Design for flat structure**: Google Sheets không có nested documents
2. **Use separate tabs**: Thay vì embed, dùng reportCode để join
3. **Batch operations**: Giảm số lần API calls
4. **Cache khi có thể**: Tránh query lặp lại
5. **Monitor rate limits**: Google có limit 100 requests/100 seconds
6. **Backup regularly**: Export sang CSV/Excel định kỳ

## 🔍 Troubleshooting

### Lỗi: "Quota exceeded"
- Đợi 100 giây rồi thử lại
- Implement rate limiting
- Giảm batch size

### Performance chậm
- Sử dụng batch operations
- Cache data
- Giảm số lần read/write

### Data không sync
- Google Sheets có eventual consistency
- Thêm delay nhỏ giữa write và read
- Verify bằng cách refresh sheet

## 📚 Resources

- [gspread Documentation](https://docs.gspread.org/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [pandas Integration](https://github.com/robin900/gspread-dataframe)

---

**Lưu ý cuối**: MongoDB vẫn tốt hơn cho production apps quy mô lớn. Google Sheets phù hợp cho:
- Prototypes
- Small teams
- Dashboard-heavy apps
- Quick internal tools
