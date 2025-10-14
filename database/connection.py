import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe
import pandas as pd
from config.settings import (
    GOOGLE_SHEETS_CREDENTIALS_FILE,
    GOOGLE_SHEETS_SPREADSHEET_ID,
    GOOGLE_SHEETS_SPREADSHEET_NAME,
    SHEET_EMPLOYEES,
    SHEET_WORK_REPORTS,
    SHEET_TASKS_ACTUAL,
    SHEET_TASKS_PLANNED,
    SHEET_REVIEWS
)


def connect_google_sheets(credentials_file: str = None, spreadsheet_id: str = None, spreadsheet_name: str = None):
    """
    Kết nối Google Sheets
    
    Args:
        credentials_file: Đường dẫn file credentials JSON
        spreadsheet_id: ID của Google Spreadsheet (optional, ưu tiên hơn name)
        spreadsheet_name: Tên của Google Spreadsheet
        
    Returns:
        (client, spreadsheet) tuple
        
    Raises:
        Exception: Nếu không thể kết nối
    """
    creds_file = credentials_file or GOOGLE_SHEETS_CREDENTIALS_FILE
    sheet_id = spreadsheet_id or GOOGLE_SHEETS_SPREADSHEET_ID
    sheet_name = spreadsheet_name or GOOGLE_SHEETS_SPREADSHEET_NAME
    
    try:
        # Define scope
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Authenticate
        creds = Credentials.from_service_account_file(creds_file, scopes=scope)
        client = gspread.authorize(creds)
        
        # Open spreadsheet
        if sheet_id:
            spreadsheet = client.open_by_key(sheet_id)
        else:
            spreadsheet = client.open(sheet_name)
        
        print(f"✓ Kết nối thành công đến Google Sheets: {spreadsheet.title}")
        
        # Initialize sheets nếu chưa có
        initialize_sheets(spreadsheet)
        
        return client, spreadsheet
        
    except FileNotFoundError:
        print(f"✗ Không tìm thấy file credentials: {creds_file}")
        print("  Hướng dẫn:")
        print("  1. Truy cập Google Cloud Console")
        print("  2. Tạo Service Account và download JSON key")
        print("  3. Đặt file JSON vào thư mục project")
        print("  4. Chia sẻ Google Sheet với email của Service Account")
        raise
    except Exception as e:
        print(f"✗ Lỗi kết nối Google Sheets: {e}")
        raise


def initialize_sheets(spreadsheet):
    """
    Khởi tạo các sheet cần thiết nếu chưa tồn tại
    
    Args:
        spreadsheet: gspread Spreadsheet object
    """
    required_sheets = {
        SHEET_EMPLOYEES: [
            "employeeCode", "fullName", "email", "departmentCode", 
            "departmentName", "position", "managerCode", "createdAt", "updatedAt"
        ],
        SHEET_WORK_REPORTS: [
            "reportCode", "employeeCode", "employeeName", "departmentCode",
            "reportPeriodYear", "reportPeriodMonth", "reportPeriodStartDate",
            "reportPeriodEndDate", "status", "version", "createdAt", "updatedAt"
        ],
        SHEET_TASKS_ACTUAL: [
            "taskId", "reportCode", "stt", "taskName", "taskType", "category",
            "startDate", "endDate", "description", "solution", "evaluation",
            "level", "parentTaskId", "hasSubtasks", "subtaskCount", "createdAt"
        ],
        SHEET_TASKS_PLANNED: [
            "taskId", "reportCode", "stt", "taskName", "taskType", "category",
            "startDate", "endDate", "description", "solution", "cost", "costUnit",
            "level", "parentTaskId", "hasSubtasks", "subtaskCount", "createdAt"
        ],
        SHEET_REVIEWS: [
            "reportCode", "dailyWorkReview", "professionalReview", "createdAt"
        ]
    }
    
    existing_sheets = [sheet.title for sheet in spreadsheet.worksheets()]
    
    for sheet_name, headers in required_sheets.items():
        if sheet_name not in existing_sheets:
            print(f"  → Tạo sheet mới: {sheet_name}")
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
            worksheet.update('A1', [headers])
            # Format header row
            worksheet.format('A1:Z1', {
                "backgroundColor": {"red": 0.2, "green": 0.6, "blue": 0.9},
                "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}
            })


def get_worksheet(spreadsheet, sheet_name: str):
    """
    Lấy worksheet theo tên
    
    Args:
        spreadsheet: gspread Spreadsheet object
        sheet_name: Tên sheet
        
    Returns:
        gspread Worksheet object
    """
    try:
        return spreadsheet.worksheet(sheet_name)
    except Exception as e:
        print(f"✗ Không tìm thấy sheet: {sheet_name}")
        raise


def test_connection(credentials_file: str = None) -> bool:
    """
    Test kết nối Google Sheets
    
    Args:
        credentials_file: Đường dẫn file credentials
        
    Returns:
        True nếu kết nối thành công
    """
    try:
        client, spreadsheet = connect_google_sheets(credentials_file)
        return True
    except:
        return False
