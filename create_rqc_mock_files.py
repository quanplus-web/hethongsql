import os
import sys
import pandas as pd
from pathlib import Path

# Fix encoding for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Import table schema mapping
from pipeline.table_schema import FILE_COLUMNS_MAPPING, normalize_name

def create_rqc_mock_files():
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
        
    generated_files = set()
    
    for sheet_name in xl.sheet_names:
        # Load sheet
        df = pd.read_excel(xl, sheet_name=sheet_name)
        
        # Get file columns for this sheet if defined, else generic scan
        file_candidates = FILE_COLUMNS_MAPPING.get(sheet_name, [])
        norm_file_candidates = [normalize_name(c) for c in file_candidates]
        
        # Find matched columns in dataframe
        matched_cols = []
        for c in df.columns:
            # Match via mapping
            if any(fc in c for fc in norm_file_candidates):
                matched_cols.append(c)
            # Or match common keywords for attachments
            elif any(k in str(c).upper() for k in ["FILE", "ATTACHMENT", "EVIDENCE", "DOCUMENT"]):
                matched_cols.append(c)
                
        matched_cols = list(set(matched_cols))
        if not matched_cols:
            continue
            
        print(f"  -> Bảng '{sheet_name}': tìm thấy cột chứa file: {matched_cols}")
        
        # Extract files
        for f_col in matched_cols:
            for val in df[f_col].dropna():
                val_str = str(val).strip()
                if not val_str or val_str.lower() in ['nan', 'none', 'null', 'http', 'https']:
                    continue
                    
                # if it is a link, skip, we only want filenames
                if val_str.startswith("http"):
                    continue
                    
                # Split by newline or comma if multiple files
                for part in val_str.replace(",", "\n").split("\n"):
                    clean_name = part.strip().split("/")[-1]
                    if clean_name and clean_name not in generated_files and "." in clean_name:
                        generated_files.add(clean_name)
                        
    print(f"[*] Đã tìm thấy tổng cộng {len(generated_files)} tên file trong RQC-CP-Database.xlsx")
    
    for fname in generated_files:
        fpath = mock_drive_dir / fname
        if not fpath.exists():
            if fname.lower().endswith(".pdf"):
                text = f"Mock file for RQC: {fname}".ljust(50, ' ')
                stream = f"BT\n/F1 14 Tf\n10 700 Td\n({text}) Tj\nET".encode('ascii', errors='ignore')
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
                fpath.write_text(f"Day la file mock tu dong tao cho RQC: {fname}", encoding="utf-8")
            
    print(f"[+] Đã tạo thành công {len(generated_files)} file giả lập (mock files) tại: {mock_drive_dir.resolve()}")

if __name__ == "__main__":
    create_rqc_mock_files()
