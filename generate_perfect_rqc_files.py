import os
import sys
import pandas as pd
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pipeline.table_schema import FILE_COLUMNS_MAPPING, normalize_name

def generate_perfect_rqc_files():
    base_dir = Path(__file__).resolve().parent
    excel_path = base_dir / "data" / "RQC-CP-Database.xlsx"
    mock_drive_dir = base_dir / "data" / "mock_drive_rqc"
    
    if not excel_path.exists():
        print(f"[-] Lỗi: Không tìm thấy file {excel_path}")
        return
        
    # Xóa sạch thư mục mock cũ để tạo lại cho chuẩn
    if mock_drive_dir.exists():
        shutil.rmtree(mock_drive_dir)
    mock_drive_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Đang đọc file Excel: {excel_path.name}")
    try:
        xl = pd.ExcelFile(excel_path)
    except Exception as e:
        print(f"[-] Lỗi đọc file Excel: {e}")
        return
        
    generated_count = 0
    
    # Chỉ duyệt qua các bảng có quy định chứa file đính kèm
    for sheet_name, file_cols in FILE_COLUMNS_MAPPING.items():
        if sheet_name not in xl.sheet_names:
            continue
            
        df = pd.read_excel(xl, sheet_name=sheet_name)
        if df.empty:
            continue
            
        first_col = df.columns[0]
        # Lấy tối đa 25 ID cho mỗi bảng để tạo mock file (tránh quá nhiều ngợp)
        sample_ids = df[first_col].dropna().astype(str).tolist()
        sample_ids = [sid for sid in sample_ids if sid and sid.lower() not in ['nan', 'none']]
        
        # Chọn file column đầu tiên làm hint (VD: ATTACHMENT, INVOICE FILE, PROCEDURE FILE)
        hint = file_cols[0] if file_cols else "FILE"
        # Bỏ dấu cách thay bằng gạch dưới cho chuẩn file name
        hint_clean = hint.replace(" ", "_")
        
        num_to_pick = min(30, len(sample_ids))
        picked_ids = sample_ids[:num_to_pick] # Lấy từ đầu cho đồng bộ
        
        print(f"  -> Bảng '{sheet_name}': Đang tạo {len(picked_ids)} files (Cột gợi ý: {hint_clean})")
        
        for rec_id in picked_ids:
            # Tạo 1 file chuẩn định dạng: ID.COLUMN_HINT.pdf
            file_name = f"{rec_id}.{hint_clean}.pdf"
            fpath = mock_drive_dir / file_name
            if not fpath.exists():
                if file_name.lower().endswith(".pdf"):
                    text = f"Mock file cho ID: {rec_id} bang {sheet_name}".ljust(60, ' ')
                    stream = f"BT\n/F1 12 Tf\n10 700 Td\n({text}) Tj\nET".encode('ascii', errors='ignore')
                    pdf = (
                        b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
                        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
                        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
                        b"4 0 obj\n<< /Length " + str(len(stream)).encode() + b" >>\nstream\n"
                        + stream + b"\nendstream\nendobj\n"
                        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\ntrailer\n<< /Size 6 /Root 1 0 R >>\n%%EOF"
                    )
                    fpath.write_bytes(pdf)
                else:
                    fpath.write_text(f"Day la file mock chuan cho ID: {rec_id} thuoc bang {sheet_name}", encoding="utf-8")
                generated_count += 1
                        
    print(f"[+] Đã tạo thành công {generated_count} file giả lập CHUẨN XÁC theo mapping ID tại: {mock_drive_dir.resolve()}")
    print(f"[+] Toàn bộ {generated_count} files này chắc chắn sẽ MAPPED 100% không bị thừa!")

if __name__ == "__main__":
    generate_perfect_rqc_files()
