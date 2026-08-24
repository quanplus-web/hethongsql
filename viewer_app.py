from flask import Flask, render_template_string, Response
import sqlite3
import os

app = Flask(__name__)

# Giao diện HTML đơn giản với 2 cột: Trái là danh sách, Phải là khung đọc PDF
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Mini Viewer App - Trải Nghiệm User</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; display: flex; height: 90vh; background: #f0f2f5; }
        .sidebar { width: 30%; border-right: 2px solid #ccc; padding-right: 20px; overflow-y: auto; }
        .viewer { width: 70%; padding-left: 20px; display: flex; flex-direction: column; }
        h2 { color: #333; margin-top: 0; }
        iframe { flex-grow: 1; border: 2px solid #ccc; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); background: #fff; }
        ul { list-style: none; padding: 0; margin: 0; }
        li { background: #fff; margin-bottom: 10px; border-radius: 6px; padding: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); transition: 0.2s; }
        li:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        a { text-decoration: none; color: #1a73e8; font-weight: bold; display: block; font-size: 14px;}
        a:hover { color: #0d47a1; }
        .meta { color: #666; font-size: 12px; margin-top: 4px; display: block; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h2>Danh sách Tài liệu</h2>
        <p style="font-size: 13px; color: #555;">Click vào một file để "nhập vai" User xem trực tiếp!</p>
        <ul>
            {% for file in files %}
            <li>
                <a href="/view/{{ file[0] }}" target="pdf_frame">
                    📄 {{ file[1] }}
                </a>
                <span class="meta">Bảng: {{ file[2] }} | ID: {{ file[3] }}</span>
            </li>
            {% endfor %}
        </ul>
    </div>
    <div class="viewer">
        <h2>Khung xem trước PDF</h2>
        <iframe name="pdf_frame" src="about:blank"></iframe>
    </div>
</body>
</html>
"""

def get_db():
    return sqlite3.connect("test_database.db")

@app.route("/")
def index():
    if not os.path.exists("test_database.db"):
        return "<h3>Lỗi: Chưa tìm thấy test_database.db! Hãy chạy lệnh 'python test_db.py' trước.</h3>", 404
        
    conn = get_db()
    cursor = conn.cursor()
    # Chỉ lấy ID và thông tin cơ bản, KHÔNG lấy file_data vì rất nặng
    cursor.execute("SELECT id, file_name, table_name, record_id FROM file_attachments ORDER BY id")
    files = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, files=files)

@app.route("/view/<int:file_id>")
def view_file(file_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_data, file_name FROM file_attachments WHERE id = ?", (file_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row[0]:
        return "Không tìm thấy dữ liệu file!", 404
        
    hex_str = row[0]
    file_name = row[1]
    
    # Do SQLite lưu mã PostgreSQL dưới dạng String, ta cắt chữ '\x' ở đầu đi
    if hex_str.startswith(r'\x'):
        hex_str = hex_str[2:]
        
    binary_data = bytes.fromhex(hex_str)
    
    # Trả về nhị phân, đặt mimetype là pdf để trình duyệt TỰ HIỂN THỊ
    return Response(
        binary_data, 
        mimetype="application/pdf", 
        headers={"Content-Disposition": f"inline; filename={file_name}"}
    )

if __name__ == "__main__":
    print("==================================================")
    print("🚀 MINI APP TRẢI NGHIỆM USER ĐÃ KHỞI ĐỘNG")
    print("👉 Mở trình duyệt và truy cập: http://127.0.0.1:5001")
    print("==================================================")
    app.run(port=5001, debug=True)
