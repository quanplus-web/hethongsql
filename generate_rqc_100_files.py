import os
import sys
import pandas as pd
import shutil
from pathlib import Path
import random

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pipeline.table_schema import FILE_COLUMNS_MAPPING, normalize_name

def generate_100_rqc_files():
    base_dir = Path(__file__).resolve().parent
    excel_path = Path(r"C:\Users\Admin\Downloads\RQC-CP-Database (1).xlsx")
    mock_drive_dir = base_dir / "data" / "mock_drive_rqc_100"
    
    if not excel_path.exists():
        print(f"[-] Lỗi: Không tìm thấy file {excel_path}")
        return
        
    if mock_drive_dir.exists():
        shutil.rmtree(mock_drive_dir)
    mock_drive_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"[*] Đang đọc file Excel dung lượng lớn (4MB): {excel_path.name}")
    try:
        # Load file excel (có thể mất vài giây)
        xl = pd.ExcelFile(excel_path)
    except Exception as e:
        print(f"[-] Lỗi đọc file Excel: {e}")
        return
        
    generated_count = 0
    
    # Số bảng cần lấy ID:
    target_tables = [t for t in FILE_COLUMNS_MAPPING.keys() if t in xl.sheet_names]
    
    # Chia đều 120 files cho các bảng có trong file (VD: 8 bảng => 15 files/bảng)
    if not target_tables:
        print("[-] Không tìm thấy bảng nào chứa cột file trong Excel này.")
        return
        
    num_per_table = max(1, 120 // len(target_tables))
    
    for sheet_name in target_tables:
        file_cols = FILE_COLUMNS_MAPPING[sheet_name]
        df = pd.read_excel(xl, sheet_name=sheet_name)
        if df.empty:
            continue
            
        first_col = df.columns[0]
        # Lấy ID và lọc các ID không hợp lệ
        sample_ids = df[first_col].dropna().astype(str).tolist()
        sample_ids = [sid for sid in sample_ids if sid and sid.lower() not in ['nan', 'none', 'null', '']]
        
        # Lấy tối đa num_per_table ID từ bảng này
        num_to_pick = min(num_per_table, len(sample_ids))
        picked_ids = random.sample(sample_ids, num_to_pick) if len(sample_ids) > num_per_table else sample_ids
        
        hint = file_cols[0] if file_cols else "FILE"
        hint_clean = hint.replace(" ", "_")
        
        print(f"  -> Bảng '{sheet_name}': Đang tạo {len(picked_ids)} files mock...")
        
        for rec_id in picked_ids:
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
                        
    print(f"[+] Đã tạo thành công {generated_count} file giả lập tại: {mock_drive_dir.resolve()}")
    print(f"[+] Toàn bộ {generated_count} files này đều khớp chính xác 100% với các ID trong file RQC!")

if __name__ == "__main__":
    generate_100_rqc_files()
