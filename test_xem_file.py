import sys
import os

def decode_hex_to_file(hex_string, output_filename):
    # Xóa ký tự \x ở đầu nếu có (định dạng của PostgreSQL)
    if hex_string.startswith('\\x'):
        hex_string = hex_string[2:]
        
    try:
        # Chuyển đổi chuỗi Hex thành dữ liệu nhị phân (bytes)
        binary_data = bytes.fromhex(hex_string)
        
        # Ghi ra file
        with open(output_filename, 'wb') as f:
            f.write(binary_data)
            
        print(f"✅ Đã giải mã thành công! File được lưu tại: {os.path.abspath(output_filename)}")
    except ValueError as e:
        print(f"❌ Lỗi: Chuỗi Hex không hợp lệ. Vui lòng kiểm tra lại copy/paste. Chi tiết: {e}")

if __name__ == "__main__":
    print("="*60)
    print("CÔNG CỤ TEST GIẢI MÃ BLOB (TỪ DATABASE) THÀNH FILE")
    print("="*60)
    
    # Yêu cầu người dùng nhập chuỗi
    print("\n👉 Hãy copy toàn bộ chuỗi '\\x...' trong ô file_data trên Supabase và dán vào đây.")
    print("(Mẹo: Trong Supabase, click đúp vào ô đó, ấn Ctrl+A rồi Ctrl+C để copy hết)")
    
    # Đọc input (có thể rất dài nên dùng sys.stdin.readline)
    hex_input = input("\nDán chuỗi Hex vào đây: ").strip()
    
    if not hex_input:
        print("Bạn chưa nhập gì cả. Thoát chương trình.")
        sys.exit(0)
        
    # Yêu cầu nhập tên file muốn xuất ra
    output_name = input("\nNhập tên file (bao gồm đuôi, ví dụ: hop_dong.pdf, anh.jpg): ").strip()
    if not output_name:
        output_name = "test_download.pdf"
        
    decode_hex_to_file(hex_input, output_name)
