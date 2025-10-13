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
from utils.features import flatten_multiindex_columns



def extract_work_report_from_excel(excel_path: str,sheet_name:str, employee_info: Dict) -> Dict:
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
    wb, sheet, title = load_excel_file(excel_path,sheet_name)
    
    # Extract report period
    report_period = extract_report_period(title)
    report_code = f"BC-{report_period['year']}-{report_period['month']:02d}-{employee_info['employeeCode']}"
    
    # Tìm vị trí sections
    sections = find_section_start_rows(sheet)
    
    # Parse tasks
    actual_functional_tasks = []
    actual_project_tasks = []
    planned_functional_tasks = []
    planned_project_tasks = []
    
    # print(wb, sheet, title)
    print("  → Đang extract Phần A: Thực hiện công việc...")
    
    if sections['actual_functional']:
        end_row = sections['actual_project'] - 1 if sections['actual_project'] else sheet.max_row
        # Section 1: Headers at rows 6-7, actual_functional data from row 9
        header_start_row = 6  # Row 6 (first header row for Section 1)
        
        # Skip rows 1-5, read headers (6,7) + data from row 9 to actual_project
        df = pd.read_excel(excel_path, sheet_name=sheet_name,
                          skiprows=list(range(0, header_start_row)),  # Skip rows 1-5
                          header=[0, 1],  # Use rows 6,7 as multi-level header
                          nrows=end_row - (header_start_row +2) + 1)  # Read from row 6 to end_row
        
        # Drop the first row after headers (row 8), keep data from row 9+
        df = df.iloc[1:]  # Skip row 8, keep data from row 9+
        
        # Flatten multi-level headers into single level
        df = flatten_multiindex_columns(df)
        
        actual_functional_tasks = parse_tasks_from_dataframe(df, "actual", "T")
        print(f"  ✓ {len(actual_functional_tasks)} công việc chức năng")
    
    # if sections['actual_project']:
    #     end_row = sections['actual_review'] - 1 if sections['actual_review'] else (sections['planned'] - 1 if sections['planned'] else sheet.max_row)
    #     # Section 1: Same headers as actual_functional (rows 6-7), but project data starts from actual_project row
    #     header_start_row = 6  # Same headers as functional section
    #     project_data_start = sections['actual_project'] + 1  # Data starts after project section header
        
    #     # Read the project section with same headers (6,7) but different data range
    #     df = pd.read_excel(excel_path, sheet_name=sheet_name,
    #                       skiprows=list(range(0, header_start_row - 1)) + list(range(header_start_row + 2, project_data_start)),
    #                       header=[0, 1],  # Use rows 6,7 as multi-level header
    #                       nrows=end_row - project_data_start + 1)  # Read project data range
        
    #     # Flatten multi-level headers into single level
    #     df = flatten_multiindex_columns(df)
        
    #     actual_project_tasks = parse_tasks_from_dataframe(df, "actual", "P")
    #     print(f"  ✓ {len(actual_project_tasks)} công việc dự án")
    
    # print("  → Đang extract Phần B: Kế hoạch công việc...")
    
    # if sections['planned_functional']:
    #     end_row = sections['planned_project'] - 1 if sections['planned_project'] else sheet.max_row
    #     # Section 2: Headers at rows 83-84, planned_functional data from row 86
    #     planned_header_start = 83  # Row 83 (first header row for Section 2)
        
    #     # Skip rows before planned headers, read headers (83,84) + data from row 86
    #     df = pd.read_excel(excel_path, sheet_name=sheet_name,
    #                       skiprows=list(range(0, planned_header_start - 1)),  # Skip rows 1-82
    #                       header=[0, 1],  # Use rows 83,84 as multi-level header
    #                       nrows=end_row - planned_header_start + 1)  # Read from row 83 to end_row
        
    #     # Drop the first row after headers (row 85), keep data from row 86+
    #     df = df.iloc[1:]  # Skip row 85, keep data from row 86+
        
    #     # Flatten multi-level headers into single level
    #     df = flatten_multiindex_columns(df)
        
    #     planned_functional_tasks = parse_tasks_from_dataframe(df, "planned", "PT")
    #     print(f"  ✓ {len(planned_functional_tasks)} công việc kế hoạch")
    
    # if sections['planned_project']:
    #     end_row = sheet.max_row
    #     # Section 2: Same headers as planned_functional (rows 83-84), but project data starts from planned_project row
    #     planned_header_start = 83  # Same headers as functional section
    #     project_data_start = sections['planned_project'] + 1  # Data starts after project section header
        
    #     # Read the project section with same headers (83,84) but different data range
    #     df = pd.read_excel(excel_path, sheet_name=sheet_name,
    #                       skiprows=list(range(0, planned_header_start - 1)) + list(range(planned_header_start + 2, project_data_start)),
    #                       header=[0, 1],  # Use rows 83,84 as multi-level header
    #                       nrows=end_row - project_data_start + 1)  # Read project data range
        
    #     # Flatten multi-level headers into single level
    #     df = flatten_multiindex_columns(df)
        
    #     planned_project_tasks = parse_tasks_from_dataframe(df, "planned", "P")
    #     print(f"  ✓ {len(planned_project_tasks)} công việc dự án kế hoạch")
    
    # Tạo work report
    # work_report = {
    #     "reportCode": report_code,
    #     # "employeeId": employee_info.get("_id"),
    #     # "employeeCode": employee_info["employeeCode"],
    #     # "employeeName": employee_info["fullName"],
    #     # "department": employee_info["department"],
    #     "reportPeriod": report_period,
    #     "actualWork": {
    #         "functionalTasks": actual_functional_tasks,
    #         "projectTasks": actual_project_tasks,
    #         "generalEvaluation": {"dailyWork": "", "professionalWork": ""}
    #     },
    #     "plannedWork": {
    #         "functionalTasks": planned_functional_tasks,
    #         "projectTasks": []
    #     },
    #     "status": DEFAULT_REPORT_STATUS,
    #     "submittedAt": None,
    #     "approvedBy": None,
    #     "approvedAt": None,
    #     "version": 1,
    #     "createdAt": datetime.now(),
    #     "updatedAt": datetime.now(),
    #     "history": [{
    #         "version": 1,
    #         "action": "imported",
    #         "changedBy": employee_info.get("_id"),
    #         "changedAt": datetime.now(),
    #         "changes": {}
    #     }]
    # }
    
    wb.close()
    return 


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
    # main()
    excel_path = './input/202509_Bao cao cong viec_thinhdv.xlsx'
    sheet_name = 'Th8-T9'
    work_report = extract_work_report_from_excel(excel_path, sheet_name, {"employeeCode":"NV001"})