"""
Main Entry Point - Work Report Processing System

Uses clean architecture with services, repositories, and parsers
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional

# Import new architecture modules
from config import Settings, setup_logging
from repositories import GoogleSheetsClient, EmployeeRepository, DepartmentRepository, ReportRepository
from services import ReportService, TaskService, ValidationService
from utils import get_logger

logger = get_logger(__name__)


def import_single_report(report_service: ReportService,
                        excel_path: str,
                        employee_code: str,
                        department_code: str,
                        auto_update: bool = False) -> Optional[Dict]:
    """
    Import a single report from Excel file
    
    Args:
        report_service: Report service instance
        excel_path: Path to Excel file
        employee_code: Employee code
        department_code: Department code
        auto_update: Whether to update existing report
        
    Returns:
        Dictionary with import results or None if failed
    """
    logger.info(f"Importing report: {excel_path}")
    print(f"\\n📄 Processing file: {excel_path}")
    
    try:
        excel_path = "./input/202509_Bao cao cong viec_thinhdv.xlsx"
        employee_code = "NV001"
        department_code = "IT"
        auto_update = True
        
        result = report_service.import_from_excel(
            file_path=excel_path,
            employee_code=employee_code,
            department_code=department_code,
            auto_update=auto_update
        )
        
        print(f"✓ Success: {result['action']} report {result['report_code']}")
        print(f"  → Period: {result['period']}")
        print(f"  → Total tasks: {result['total_tasks']}")
        print(f"  → Task breakdown:")
        for task_type, count in result['task_counts'].items():
            print(f"    - {task_type}: {count}")
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to import report: {e}")
        print(f"✗ Error: {e}")
        return None


def import_batch_reports(report_service: ReportService,
                        excel_files: List[str],
                        employee_codes: List[str],
                        department_codes: List[str],
                        auto_update: bool = False):
    """
    Import multiple reports
    
    Args:
        report_service: Report service instance
        excel_files: List of Excel file paths
        employee_codes: List of employee codes
        department_codes: List of department codes
        auto_update: Whether to update existing reports
    """
    if not (len(excel_files) == len(employee_codes) == len(department_codes)):
        print("✗ Error: Number of files, employees, and departments must match")
        return
    
    print(f"\\n🚀 Starting batch import of {len(excel_files)} reports...")
    
    success = 0
    failed = 0
    results = []
    
    for excel_file, emp_code, dept_code in zip(excel_files, employee_codes, department_codes):
        result = import_single_report(
            report_service,
            excel_file,
            emp_code,
            dept_code,
            auto_update
        )
        
        if result:
            success += 1
            results.append(result)
        else:
            failed += 1
    
    print(f"\\n📊 Results: ✓ {success} successful, ✗ {failed} failed")
    return results


def view_report_summary(report_service: ReportService, report_code: str):
    """View summary of a report"""
    print(f"\\n📋 Report Summary: {report_code}")
    
    summary = report_service.get_report_summary(report_code)
    
    if not summary:
        print(f"✗ Report not found: {report_code}")
        return
    
    report = summary['report']
    counts = summary['task_counts']
    
    print(f"\\nEmployee: {report['employee_name']} ({report['employee_code']})")
    print(f"Period: {report['period']['year']}-{report['period']['month']:02d}")
    print(f"Status: {report['status']}")
    print(f"Version: {report['version']}")
    
    print(f"\\nTask Counts:")
    print(f"  Actual Functional: {counts['actual_functional']}")
    print(f"  Actual Project: {counts['actual_project']}")
    print(f"  Planned Functional: {counts['planned_functional']}")
    print(f"  Planned Project: {counts['planned_project']}")
    print(f"  Has Review: {'Yes' if summary['has_review'] else 'No'}")


def run_validation(client: GoogleSheetsClient):
    """Run validation checks on all data"""
    print("\\n🔍 Running validation checks...")
    
    validation_service = ValidationService(
        EmployeeRepository(client),
        DepartmentRepository(client),
        ReportRepository(client)
    )
    
    report = validation_service.get_validation_report()
    
    print(f"\\n📊 Validation Summary:")
    print(f"  Total Issues: {report['summary']['total_issues']}")
    print(f"  Orphaned Employees: {report['summary']['orphaned_employees_count']}")
    print(f"  Empty Departments: {report['summary']['empty_departments_count']}")
    print(f"  Duplicate Reports: {report['summary']['duplicate_reports_count']}")
    
    if report['summary']['total_issues'] > 0:
        print(f"\\n⚠️  Issues Found:")
        
        for orphan in report['issues']['orphaned_employees']:
            print(f"  - Employee {orphan['employee_code']} references non-existent department {orphan['department_code']}")
        
        for dept in report['issues']['empty_departments']:
            print(f"  - Department {dept} has no employees")
        
        for dup in report['issues']['duplicate_reports']:
            print(f"  - Duplicate report for {dup['employee_code']} in {dup['period']}")


def create_cli_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Work Report Processing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import a single report
  python main.py import --file report.xlsx --employee NV001 --department IT
  
  # Import with auto-update
  python main.py import --file report.xlsx --employee NV001 --department IT --auto-update
  
  # View report summary
  python main.py view --report RPT-NV001-202409
  
  # Run validation
  python main.py validate
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import report from Excel')
    import_parser.add_argument('--file', '-f', required=True, help='Excel file path')
    import_parser.add_argument('--employee', '-e', required=True, help='Employee code')
    import_parser.add_argument('--department', '-d', required=True, help='Department code')
    import_parser.add_argument('--auto-update', '-u', action='store_true', help='Auto-update existing report')
    
    # Batch import command
    batch_parser = subparsers.add_parser('batch', help='Import multiple reports')
    batch_parser.add_argument('--files', '-f', nargs='+', required=True, help='Excel file paths')
    batch_parser.add_argument('--employees', '-e', nargs='+', required=True, help='Employee codes')
    batch_parser.add_argument('--departments', '-d', nargs='+', required=True, help='Department codes')
    batch_parser.add_argument('--auto-update', '-u', action='store_true', help='Auto-update existing reports')
    
    # View command
    view_parser = subparsers.add_parser('view', help='View report summary')
    view_parser.add_argument('--report', '-r', required=True, help='Report code')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Run validation checks')
    
    return parser


def main():
    """Main entry point"""
    # Setup
    setup_logging()
    settings = Settings()
    
    # Validate settings
    is_valid, error = settings.validate()
    if not is_valid:
        logger.error(f"Invalid settings: {error}")
        print(f"✗ Configuration error: {error}")
        sys.exit(1)
    
    # Parse arguments
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        # Initialize client
        logger.info("Connecting to Google Sheets...")
        client = GoogleSheetsClient(settings)
        
        if not client.test_connection():
            print("✗ Failed to connect to Google Sheets")
            sys.exit(1)
        
        print("✓ Connected to Google Sheets")
        
        # Initialize service
        report_service = ReportService(client)
        
        # Execute command
        if args.command == 'import':
            import_single_report(
                report_service,
                args.file,
                args.employee,
                args.department,
                args.auto_update
            )
        
        elif args.command == 'batch':
            import_batch_reports(
                report_service,
                args.files,
                args.employees,
                args.departments,
                args.auto_update
            )
        
        elif args.command == 'view':
            view_report_summary(report_service, args.report)
        
        elif args.command == 'validate':
            run_validation(client)
        
        print("\\n✓ Complete")
        
    except KeyboardInterrupt:
        print("\\n\\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\\n✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # main()
    import_single_report(
        ReportService(GoogleSheetsClient(Settings())),
        "./input/202509_Bao cao cong viec_thinhdv.xlsx",
        "NV001",
        "IT",
        auto_update=False
    )
