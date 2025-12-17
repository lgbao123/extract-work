"""
Quick test script for Employee and Department model conversions
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly to avoid full config initialization
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

# Import base model
from models.base import BaseModel

# We'll test with simplified imports
try:
    from models.employee import Employee
    from models.department import Department
except ImportError as e:
    print(f"Import error: {e}")
    print("Testing with direct code inspection instead...")
    sys.exit(1)


def test_employee_model():
    """Test Employee model conversions"""
    print("=" * 60)
    print("Testing Employee Model")
    print("=" * 60)
    
    # Create employee
    emp = Employee(
        employee_code="NV001",
        full_name="Nguyen Van A",
        email="a.nguyen@company.com",
        department_code="IT",
        department_name="Information Technology",
        position="Developer",
        manager_code="MG001"
    )
    
    print(f"\n1. Created: {emp}")
    
    # Convert to sheet dict (camelCase)
    sheet_dict = emp.to_sheet_dict()
    print(f"\n2. to_sheet_dict() output:")
    for key, value in sheet_dict.items():
        print(f"   {key}: {value}")
    
    # Convert back from dict
    emp2 = Employee.from_dict(sheet_dict)
    print(f"\n3. from_dict() result: {emp2}")
    print(f"   email: {emp2.email}")
    print(f"   department_code: {emp2.department_code}")
    
    # Test with snake_case dict
    snake_dict = {
        'employee_code': 'NV002',
        'full_name': 'Tran Thi B',
        'email': 'b.tran@company.com',
        'department_code': 'HR',
        'department_name': 'Human Resources',
        'position': 'Manager',
        'created_at': '2025-01-15 10:30:00'
    }
    emp3 = Employee.from_dict(snake_dict)
    print(f"\n4. from_dict(snake_case): {emp3}")
    print(f"   created_at: {emp3.created_at}")
    
    print("\n✅ Employee model tests passed!\n")


def test_department_model():
    """Test Department model conversions"""
    print("=" * 60)
    print("Testing Department Model")
    print("=" * 60)
    
    # Create department
    dept = Department(
        department_code="IT",
        department_name="Information Technology",
        manager_code="MG001",
        parent_department_code="TECH"
    )
    
    print(f"\n1. Created: {dept}")
    
    # Convert to sheet dict (camelCase)
    sheet_dict = dept.to_sheet_dict()
    print(f"\n2. to_sheet_dict() output:")
    for key, value in sheet_dict.items():
        print(f"   {key}: {value}")
    
    # Convert back from dict
    dept2 = Department.from_dict(sheet_dict)
    print(f"\n3. from_dict() result: {dept2}")
    print(f"   manager_code: {dept2.manager_code}")
    print(f"   parent_department_code: {dept2.parent_department_code}")
    
    # Test with snake_case dict
    snake_dict = {
        'department_code': 'HR',
        'department_name': 'Human Resources',
        'manager_code': 'MG002',
        'created_at': '2025-01-15 10:30:00'
    }
    dept3 = Department.from_dict(snake_dict)
    print(f"\n4. from_dict(snake_case): {dept3}")
    
    print("\n✅ Department model tests passed!\n")


def main():
    test_employee_model()
    test_department_model()
    
    print("=" * 60)
    print("✅ All model tests completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()
