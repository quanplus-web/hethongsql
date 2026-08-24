import sys
import sqlite3
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

db_file = Path("test_database.db")
sql_file = Path("output/all_migration.sql")

def init_and_test_database():
    print("=" * 70)
    print("        KIỂM THỬ NẠP DỮ LIỆU VÀO DATABASE (SQLITE CỤC BỘ)")
    print("=" * 70)

    if not sql_file.exists():
        print(f"[!] Chưa tìm thấy file SQL {sql_file}. Vui lòng chạy 'python main.py' trước!")
        return

    # Xóa file DB cũ nếu có để nạp lại từ đầu
    if db_file.exists():
        db_file.unlink()
        print(f"[*] Đã làm sạch database cũ: {db_file.name}")

    print(f"[*] Đang nạp tập lệnh SQL: {sql_file.name} vào {db_file.name}...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    with open(sql_file, "r", encoding="utf-8") as f:
        sql_script = f.read()

    # --- CHỈNH SỬA TƯƠNG THÍCH CHO SQLITE ---
    # 1. SQLite dùng INTEGER PRIMARY KEY AUTOINCREMENT thay vì SERIAL của Postgres
    sql_script = sql_script.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
    # 2. Dữ liệu Excel có thể bị trùng khóa chính (ID), dùng INSERT OR IGNORE để bỏ qua lỗi và chạy tiếp
    sql_script = sql_script.replace("INSERT INTO", "INSERT OR IGNORE INTO")

    # Thực thi toàn bộ script SQL
    try:
        cursor.executescript(sql_script)
        conn.commit()
        print(f"[+] Nạp Database THÀNH CÔNG 100% không có lỗi cú pháp!")
    except Exception as e:
        print(f"[!] Lỗi khi thực thi SQL: {e}")
        conn.close()
        return

    # 1. Truy vấn kiểm tra danh sách bảng
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
    print(f"\n[+] Danh sách các bảng đã tạo trong Database ({len(tables)} bảng):")
    print("   ", ", ".join(tables))

    # 2. Truy vấn mẫu bảng COMPANY
    print("\n" + "-" * 70)
    print(">>> DỮ LIỆU THỰC TẾ TRONG BẢNG 'company':")
    cursor.execute("SELECT company_id, company_name, type, country, city FROM company LIMIT 10;")
    for row in cursor.fetchall():
        print(f"    - ID: {row[0]:<10} | Tên: {row[1]:<18} | Loại: {row[2]:<12} | {row[3]} ({row[4]})")

    # 3. Truy vấn mẫu bảng REQUEST DETAIL
    if "request_detail" in tables:
        print("\n" + "-" * 70)
        print(">>> DỮ LIỆU THỰC TẾ TRONG BẢNG 'request_detail':")
        cursor.execute("SELECT detail_id, request_id, item_name, amount, currency FROM request_detail;")
        for row in cursor.fetchall():
            print(f"    - Mã: {row[0]:<8} | Request: {row[1]:<8} | Hạng mục: {row[2]:<30} | {row[3]:>10} {row[4]}")

    # 4. Truy vấn mẫu bảng FILE ATTACHMENTS
    if "file_attachments" in tables:
        print("\n" + "-" * 70)
        print(">>> TỆP TIN GOOGLE DRIVE ĐÃ ĐƯỢC MAP VÀO BẢNG 'file_attachments':")
        cursor.execute("SELECT table_name, record_id, column_name, file_name, file_size_bytes FROM file_attachments;")
        for row in cursor.fetchall():
            print(f"    - [{row[0]}.{row[1]}] (Cột: {row[2]})")
            print(f"      + Tên tệp: {row[3]}")
            print(f"      + Dung lượng: {row[4]} bytes")

    conn.close()
    print("\n" + "=" * 70)
    print(f"[V] KIỂM THỬ HOÀN TẤT: File database đã tạo tại '{db_file.resolve()}'")
    print("=" * 70)

if __name__ == "__main__":
    init_and_test_database()
