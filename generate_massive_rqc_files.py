import os
import sys
import pandas as pd
from pathlib import Path
import random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def generate_massive_rqc_files():
    base_dir = Path(__file__).resolve().parent
    excel_path = base_dir / "data" / "RQC-CP-Database.xlsx"
    mock_drive_dir = base_dir / "data" / "mock_drive_rqc"
    
    if not excel_path.exists():
        print(f"[-] Lỗi: Không tìm thấy file {excel_path}")
        return
        
    mock_drive_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Đang đọc file Excel: {excel_path.name}")
    try:
        xl = pd.ExcelFile(excel_path)
    except Exception as e:
        print(f"[-] Lỗi đọc file Excel: {e}")
        return
        
    generated_count = 0
    
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet_name)
        if df.empty:
            continue
            
        first_col = df.columns[0]
        
        # Lấy tối đa 10 ID từ mỗi bảng để tạo file cho đỡ quá tải (có 30 bảng => ~300 files)
        sample_ids = df[first_col].dropna().astype(str).tolist()
        sample_ids = [sid for sid in sample_ids if sid and sid.lower() not in ['nan', 'none']]
        
        # Chọn ngẫu nhiên khoảng 3-5 ID mỗi bảng để tạo mock file
        num_to_pick = min(5, len(sample_ids))
        if num_to_pick > 0:
            picked_ids = random.sample(sample_ids, num_to_pick)
            for rec_id in picked_ids:
                # Tạo 1-2 file cho mỗi ID
                num_files = random.randint(1, 2)
                for i in range(num_files):
                    file_name = f"{rec_id}.DOCUMENT.mock_file_{random.randint(100, 999)}.pdf"
                    fpath = mock_drive_dir / file_name
                    if not fpath.exists():
                        # Cấu trúc mã hóa file PDF cơ bản để mở được bằng Chrome/Acrobat
                        text = f"Mock PDF for ID: {rec_id}".ljust(50, ' ')
                        stream_content = f"BT\n/F1 18 Tf\n10 700 Td\n({text}) Tj\nET".encode('ascii', errors='ignore')
                        pdf_content = (
                            b"%PDF-1.4\n"
                            b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
                            b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
                            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
                            b"4 0 obj\n<< /Length " + str(len(stream_content)).encode() + b" >>\nstream\n"
                            + stream_content + b"\nendstream\nendobj\n"
                            b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
                            b"trailer\n<< /Size 6 /Root 1 0 R >>\n%%EOF"
                        )
                        fpath.write_bytes(pdf_content)
                        generated_count += 1
                        
    print(f"[+] Đã tạo thành công {generated_count} file giả lập hàng loạt tại: {mock_drive_dir.resolve()}")
    print(f"[+] Tổng số file hiện có trong thư mục: {len(list(mock_drive_dir.glob('*')))}")

if __name__ == "__main__":
    generate_massive_rqc_files()
