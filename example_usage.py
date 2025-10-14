"""
Example: Import báo cáo vào Google Sheets

Script mẫu để import báo cáo công việc từ Excel vào Google Sheets
"""

from database.connection import connect_google_sheets
from database.operations import insert_employee, get_employee_by_code
from main import extract_work_report_from_excel

def example_import_single_report():
    """Example: Import 1 báo cáo"""
    
    print("=" * 60)
    print("📝 EXAMPLE: Import một báo cáo")
    print("=" * 60)
    print()
    
    # Bước 1: Kết nối Google Sheets
    print("🔌 Bước 1: Kết nối Google Sheets...")
    client, spreadsheet = connect_google_sheets()
    print()
    
    # Bước 2: Thêm thông tin nhân viên (nếu chưa có)
    print("👤 Bước 2: Thêm thông tin nhân viên...")
    employee_data = {
        "employeeCode": "NV001",
        "fullName": "Nguyễn Văn A",
        "email": "a.nguyen@company.com",
        "departmentCode": "IT",
        "departmentName": "Phòng Công nghệ thông tin",
        "position": "Developer",
        "managerCode": "NV000"
    }
    
    # Kiểm tra nhân viên đã tồn tại chưa
    existing = get_employee_by_code(spreadsheet, employee_data["employeeCode"])
    if existing:
        print(f"→ Nhân viên {employee_data['employeeCode']} đã tồn tại")
    else:
        insert_employee(spreadsheet, employee_data)
    print()
    
    # Bước 3: Extract và import báo cáo
    print("📄 Bước 3: Extract và import báo cáo...")
    excel_path = "./input/202509_Bao cao cong viec_thinhdv.xlsx"
    sheet_name = "Th8-T9"
    
    try:
        # Extract work report from Excel
        work_report = extract_work_report_from_excel(
            excel_path, 
            sheet_name, 
            employee_data
        )
        
        # Import vào Google Sheets
        from database.operations import insert_work_report
        success = insert_work_report(spreadsheet, work_report, auto_update=True)
        
        if success:
            print()
            print("=" * 60)
            print("✅ IMPORT THÀNH CÔNG!")
            print("=" * 60)
            print()
            print(f"📊 Spreadsheet: {spreadsheet.title}")
            print(f"🔗 URL: {spreadsheet.url}")
            print()
            print("📋 Dữ liệu đã được lưu vào các sheet:")
            print("  • Employees - Thông tin nhân viên")
            print("  • Work_Reports - Báo cáo tổng quan")
            print("  • Tasks_Actual - Công việc đã thực hiện")
            print("  • Tasks_Planned - Công việc kế hoạch")
            print("  • Reviews - Đánh giá chung")
            print()
        else:
            print("⚠️ Import bị hủy hoặc thất bại")
            
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {excel_path}")
        print(f"   Vui lòng đặt file Excel vào thư mục: ./input/")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()


def example_import_batch_reports():
    """Example: Import nhiều báo cáo"""
    
    print("=" * 60)
    print("📝 EXAMPLE: Import nhiều báo cáo (batch)")
    print("=" * 60)
    print()
    
    # Kết nối
    print("🔌 Kết nối Google Sheets...")
    client, spreadsheet = connect_google_sheets()
    print()
    
    # Danh sách file và nhân viên
    batch_data = [
        {
            "excel_path": "./input/baocao_NV001.xlsx",
            "sheet_name": "Th8-T9",
            "employee": {
                "employeeCode": "NV001",
                "fullName": "Nguyễn Văn A",
                "email": "a.nguyen@company.com",
                "departmentCode": "IT",
                "departmentName": "Phòng CNTT",
                "position": "Developer",
                "managerCode": "NV000"
            }
        },
        {
            "excel_path": "./input/baocao_NV002.xlsx",
            "sheet_name": "Th8-T9",
            "employee": {
                "employeeCode": "NV002",
                "fullName": "Trần Thị B",
                "email": "b.tran@company.com",
                "departmentCode": "IT",
                "departmentName": "Phòng CNTT",
                "position": "Tester",
                "managerCode": "NV000"
            }
        }
    ]
    
    print(f"📦 Đang import {len(batch_data)} báo cáo...")
    print()
    
    success_count = 0
    failed_count = 0
    
    for i, item in enumerate(batch_data, 1):
        print(f"[{i}/{len(batch_data)}] Processing {item['employee']['employeeCode']}...")
        
        try:
            # Insert employee
            insert_employee(spreadsheet, item['employee'])
            
            # Extract report
            work_report = extract_work_report_from_excel(
                item['excel_path'],
                item['sheet_name'],
                item['employee']
            )
            
            # Insert report
            from database.operations import insert_work_report
            if insert_work_report(spreadsheet, work_report, auto_update=True):
                success_count += 1
                print(f"  ✓ Thành công")
            else:
                failed_count += 1
                print(f"  ✗ Thất bại")
                
        except Exception as e:
            failed_count += 1
            print(f"  ✗ Lỗi: {e}")
        
        print()
    
    print("=" * 60)
    print(f"📊 KẾT QUẢ: {success_count} thành công, {failed_count} thất bại")
    print("=" * 60)


def example_query_data():
    """Example: Query dữ liệu từ Google Sheets"""
    
    print("=" * 60)
    print("🔍 EXAMPLE: Query dữ liệu")
    print("=" * 60)
    print()
    
    # Kết nối
    client, spreadsheet = connect_google_sheets()
    
    from database.operations import (
        get_employee_by_code,
        get_reports_by_employee,
        get_reports_by_department
    )
    
    # Query 1: Lấy thông tin nhân viên
    print("1️⃣ Lấy thông tin nhân viên NV001:")
    employee = get_employee_by_code(spreadsheet, "NV001")
    if employee:
        print(f"   Họ tên: {employee.get('fullName')}")
        print(f"   Email: {employee.get('email')}")
        print(f"   Phòng ban: {employee.get('departmentName')}")
    else:
        print("   Không tìm thấy")
    print()
    
    # Query 2: Lấy báo cáo của nhân viên
    print("2️⃣ Lấy báo cáo của NV001 trong tháng 9/2025:")
    reports = get_reports_by_employee(spreadsheet, "NV001", year=2025, month=9)
    print(f"   Tìm thấy: {len(reports)} báo cáo")
    for report in reports:
        print(f"   - {report.get('reportCode')}")
    print()
    
    # Query 3: Lấy báo cáo của phòng ban
    print("3️⃣ Lấy tất cả báo cáo của phòng IT:")
    dept_reports = get_reports_by_department(spreadsheet, "IT", year=2025)
    print(f"   Tìm thấy: {len(dept_reports)} báo cáo")
    print()
    
    print("=" * 60)
    print("✅ Query hoàn tất!")
    print("=" * 60)


def main():
    """Main menu"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "GOOGLE SHEETS WORK REPORT SYSTEM" + " " * 16 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    print("Chọn example để chạy:")
    print()
    print("  1. Import một báo cáo")
    print("  2. Import nhiều báo cáo (batch)")
    print("  3. Query dữ liệu")
    print("  0. Thoát")
    print()
    
    choice = input("Nhập lựa chọn (0-3): ").strip()
    
    if choice == "1":
        example_import_single_report()
    elif choice == "2":
        example_import_batch_reports()
    elif choice == "3":
        example_query_data()
    elif choice == "0":
        print("👋 Tạm biệt!")
    else:
        print("❌ Lựa chọn không hợp lệ")


if __name__ == "__main__":
    main()
