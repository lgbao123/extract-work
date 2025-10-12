import sys
from datetime import datetime
from typing import List, Dict
import pandas as pd

# Import các module
from config.settings import DEFAULT_REPORT_STATUS
from database.connection import connect_mongodb, close_mongodb
from database.operations import insert_employee, insert_work_report
from extractors.excel_reader import load_excel_file, find_section_start_rows
from extractors.task_parser import parse_tasks_from_dataframe
from utils.parsers import extract_report_period
from utils.validators import validate_employee_data, validate_work_report


def extract_work_report_from_excel(excel_path: str, employee_info: Dict) -> Dict:
    """
    Extract báo cáo công việc từ file Excel
    
    Args:
        excel_path: Đường dẫn file Excel
        employee_info: Thông tin nhân viên
        
    Returns:
        Dict work report
    """
    print(f"\\n📄 Đang xử lý file: {excel_path}")
    
    # Load Excel
    wb, sheet, title = load_excel_file(excel_path)
    
    # Extract report period
    report_period = extract_report_period(title)
    report_code = f"BC-{report_period['year']}-{report_period['month']:02d}-{employee_info['employeeCode']}"
    
    # Tìm vị trí sections
    sections = find_section_start_rows(sheet)
    
    # Parse tasks
    actual_functional_tasks = []
    actual_project_tasks = []
    planned_functional_tasks = []
    
    print("  → Đang extract Phần A: Thực hiện công việc...")
    
    if sections['actual_functional']:
        end_row = sections['actual_project'] - 3 if sections['actual_project'] else sheet.max_row
        df = pd.read_excel(excel_path, sheet_name=0, 
                          skiprows=sections['actual_functional']-1, 
                          nrows=end_row - sections['actual_functional'] + 1)
        actual_functional_tasks = parse_tasks_from_dataframe(df, "actual", "T")
        print(f"  ✓ {len(actual_functional_tasks)} công việc chức năng")
    
    if sections['actual_project']:
        end_row = sections['planned_functional'] - 5 if sections['planned_functional'] else sheet.max_row
        df = pd.read_excel(excel_path, sheet_name=0,
                          skiprows=sections['actual_project']-1,
                          nrows=end_row - sections['actual_project'] + 1)
        actual_project_tasks = parse_tasks_from_dataframe(df, "actual", "P")
        print(f"  ✓ {len(actual_project_tasks)} công việc dự án")
    
    print("  → Đang extract Phần B: Kế hoạch công việc...")
    
    if sections['planned_functional']:
        df = pd.read_excel(excel_path, sheet_name=0,
                          skiprows=sections['planned_functional']-1,
                          nrows=20)
        planned_functional_tasks = parse_tasks_from_dataframe(df, "planned", "PT")
        print(f"  ✓ {len(planned_functional_tasks)} công việc kế hoạch")
    
    # Tạo work report
    work_report = {
        "reportCode": report_code,
        "employeeId": employee_info.get("_id"),
        "employeeCode": employee_info["employeeCode"],
        "employeeName": employee_info["fullName"],
        "department": employee_info["department"],
        "reportPeriod": report_period,
        "actualWork": {
            "functionalTasks": actual_functional_tasks,
            "projectTasks": actual_project_tasks,
            "generalEvaluation": {"dailyWork": "", "professionalWork": ""}
        },
        "plannedWork": {
            "functionalTasks": planned_functional_tasks,
            "projectTasks": []
        },
        "status": DEFAULT_REPORT_STATUS,
        "submittedAt": None,
        "approvedBy": None,
        "approvedAt": None,
        "version": 1,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "history": [{
            "version": 1,
            "action": "imported",
            "changedBy": employee_info.get("_id"),
            "changedAt": datetime.now(),
            "changes": {}
        }]
    }
    
    wb.close()
    return work_report


def import_single_report(db, excel_path: str, employee_data: Dict):
    """Import một báo cáo"""
    # Validate
    is_valid, error = validate_employee_data(employee_data)
    if not is_valid:
        print(f"✗ Dữ liệu nhân viên không hợp lệ: {error}")
        return False
    
    # Insert employee
    employee = insert_employee(db, employee_data)
    
    # Extract report
    work_report = extract_work_report_from_excel(excel_path, employee)
    
    # Validate report
    is_valid, error = validate_work_report(work_report)
    if not is_valid:
        print(f"✗ Dữ liệu báo cáo không hợp lệ: {error}")
        return False
    
    # Insert report
    return insert_work_report(db, work_report)


def import_batch_reports(db, excel_files: List[str], employees: List[Dict]):
    """Import nhiều báo cáo"""
    if len(excel_files) != len(employees):
        raise ValueError("Số lượng file và nhân viên phải bằng nhau")
    
    print(f"\\n🚀 Bắt đầu import {len(excel_files)} báo cáo...")
    
    success = 0
    failed = 0
    
    for excel_file, employee_data in zip(excel_files, employees):
        try:
            if import_single_report(db, excel_file, employee_data):
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Lỗi: {e}")
            failed += 1
    
    print(f"\\n📊 Kết quả: ✓ {success} thành công, ✗ {failed} thất bại")


def main():
    """Entry point"""
    # Kết nối DB
    client, db = connect_mongodb()
    
    try:
        # Dữ liệu mẫu
        employee = {
            "employeeCode": "NV001",
            "fullName": "Nguyễn Khắc Trung",
            "email": "trung@company.com",
            "department": {"code": "IT", "name": "Phòng CNTT"},
            "position": {"code": "LEADER", "name": "Trưởng nhóm"},
            "status": "active",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        excel_files = ["reports/baocao_NV001.xlsx"]
        
        # Import một file
        import_single_report(db, excel_files[0], employee)
        
        # Hoặc import nhiều file
        # import_batch_reports(db, excel_files, [employee])
        
    finally:
        close_mongodb(client)


if __name__ == "__main__":
    main()