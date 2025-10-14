"""
Test Google Sheets Connection

Chạy script này để kiểm tra kết nối với Google Sheets
"""

from database.connection import test_connection, connect_google_sheets

def main():
    print("=" * 60)
    print("🧪 TESTING GOOGLE SHEETS CONNECTION")
    print("=" * 60)
    print()
    
    print("📝 Kiểm tra:")
    print("  1. File credentials.json có tồn tại?")
    print("  2. Google Sheets API đã được enable?")
    print("  3. Spreadsheet đã được share với Service Account?")
    print()
    
    print("🔌 Đang kết nối...")
    
    try:
        client, spreadsheet = connect_google_sheets()
        
        print()
        print("✅ KẾT NỐI THÀNH CÔNG!")
        print()
        print(f"📊 Spreadsheet: {spreadsheet.title}")
        print(f"📍 URL: {spreadsheet.url}")
        print()
        
        # List existing sheets
        worksheets = spreadsheet.worksheets()
        print(f"📋 Các sheet hiện có ({len(worksheets)}):")
        for ws in worksheets:
            print(f"  - {ws.title}")
        
        print()
        print("=" * 60)
        print("🎉 HỆ THỐNG SẴN SÀNG SỬ DỤNG!")
        print("=" * 60)
        print()
        print("📖 Bước tiếp theo:")
        print("  1. Import báo cáo: python main.py")
        print("  2. Xem README_GOOGLE_SHEETS.md để biết thêm chi tiết")
        print()
        
        return True
        
    except FileNotFoundError as e:
        print()
        print("❌ LỖI: Không tìm thấy file credentials.json")
        print()
        print("🔧 Cách khắc phục:")
        print("  1. Download Service Account JSON key từ Google Cloud Console")
        print("  2. Đổi tên thành 'credentials.json'")
        print("  3. Đặt file vào thư mục project")
        print()
        print(f"📂 Thư mục hiện tại: {os.getcwd()}")
        print()
        return False
        
    except Exception as e:
        print()
        print(f"❌ LỖI: {e}")
        print()
        print("🔧 Các nguyên nhân có thể:")
        print("  1. Chưa enable Google Sheets API")
        print("  2. Chưa share spreadsheet với Service Account")
        print("  3. Spreadsheet ID sai")
        print("  4. Credentials file không hợp lệ")
        print()
        print("📖 Xem chi tiết: SETUP_GUIDE.md")
        print()
        return False


if __name__ == "__main__":
    import os
    main()
