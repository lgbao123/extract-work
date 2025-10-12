from datetime import datetime
from typing import Dict, List, Optional
from pymongo.errors import DuplicateKeyError
from config.settings import (
    COLLECTION_EMPLOYEES,
    COLLECTION_WORK_REPORTS,
    DEFAULT_REPORT_STATUS
)


def insert_employee(db, employee_data: Dict) -> Dict:
    """
    Thêm nhân viên mới hoặc lấy thông tin nếu đã tồn tại
    
    Args:
        db: MongoDB database
        employee_data: Dict thông tin nhân viên
        
    Returns:
        Dict employee với _id
    """
    try:
        result = db[COLLECTION_EMPLOYEES].insert_one(employee_data)
        employee_data["_id"] = result.inserted_id
        print(f"✓ Đã thêm nhân viên: {employee_data['employeeCode']} - {employee_data['fullName']}")
        return employee_data
    except DuplicateKeyError:
        existing = db[COLLECTION_EMPLOYEES].find_one({
            "employeeCode": employee_data["employeeCode"]
        })
        print(f"→ Nhân viên đã tồn tại: {employee_data['employeeCode']}")
        return existing


def get_employee_by_code(db, employee_code: str) -> Optional[Dict]:
    """
    Lấy thông tin nhân viên theo mã
    
    Args:
        db: MongoDB database
        employee_code: Mã nhân viên
        
    Returns:
        Dict employee hoặc None
    """
    return db[COLLECTION_EMPLOYEES].find_one({"employeeCode": employee_code})


def insert_work_report(db, work_report: Dict, auto_update: bool = False) -> bool:
    """
    Thêm báo cáo công việc
    
    Args:
        db: MongoDB database
        work_report: Dict báo cáo
        auto_update: Tự động update nếu đã tồn tại
        
    Returns:
        True nếu thành công
    """
    try:
        existing = db[COLLECTION_WORK_REPORTS].find_one({
            "reportCode": work_report["reportCode"]
        })
        
        if existing:
            print(f"⚠ Báo cáo đã tồn tại: {work_report['reportCode']}")
            
            if auto_update:
                should_update = True
            else:
                choice = input("  Bạn có muốn cập nhật? (y/n): ")
                should_update = choice.lower() == 'y'
            
            if should_update:
                work_report["version"] = existing.get("version", 1) + 1
                work_report["updatedAt"] = datetime.now()
                work_report["history"] = existing.get("history", []) + work_report.get("history", [])
                
                db[COLLECTION_WORK_REPORTS].update_one(
                    {"reportCode": work_report["reportCode"]},
                    {"$set": work_report}
                )
                print(f"✓ Đã cập nhật báo cáo: {work_report['reportCode']}")
                return True
            else:
                return False
        else:
            db[COLLECTION_WORK_REPORTS].insert_one(work_report)
            print(f"✓ Đã import báo cáo: {work_report['reportCode']}")
            return True
            
    except Exception as e:
        print(f"✗ Lỗi import báo cáo: {e}")
        return False


def get_work_report_by_code(db, report_code: str) -> Optional[Dict]:
    """
    Lấy báo cáo theo mã
    
    Args:
        db: MongoDB database
        report_code: Mã báo cáo
        
    Returns:
        Dict report hoặc None
    """
    return db[COLLECTION_WORK_REPORTS].find_one({"reportCode": report_code})


def get_reports_by_employee(db, employee_code: str, year: int = None, month: int = None) -> List[Dict]:
    """
    Lấy danh sách báo cáo của nhân viên
    
    Args:
        db: MongoDB database
        employee_code: Mã nhân viên
        year: Năm (optional)
        month: Tháng (optional)
        
    Returns:
        List các báo cáo
    """
    query = {"employeeCode": employee_code}
    
    if year:
        query["reportPeriod.year"] = year
    if month:
        query["reportPeriod.month"] = month
    
    return list(db[COLLECTION_WORK_REPORTS].find(query).sort("reportPeriod.startDate", -1))


def get_reports_by_department(db, department_code: str, year: int = None, month: int = None) -> List[Dict]:
    """
    Lấy danh sách báo cáo của phòng ban
    
    Args:
        db: MongoDB database
        department_code: Mã phòng ban
        year: Năm (optional)
        month: Tháng (optional)
        
    Returns:
        List các báo cáo
    """
    query = {"department.code": department_code}
    
    if year:
        query["reportPeriod.year"] = year
    if month:
        query["reportPeriod.month"] = month
    
    return list(db[COLLECTION_WORK_REPORTS].find(query))