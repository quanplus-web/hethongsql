import re
from typing import Dict, List, Tuple
import pandas as pd
from pipeline.table_schema import FILE_COLUMNS_MAPPING, normalize_name

def extract_id_from_filename(filename: str) -> Tuple[str, str]:
    """
    Bóc tách mã ID bản ghi và tên cột từ tên file trên Google Drive.
    Ví dụ: '00d30875.PROCEDURE FILE.094814.xlsm - Procurement.pdf'
    -> (id: '00d30875', col_hint: 'procedure_file')
    """
    if not filename:
        return "", ""
    
    parts = filename.split(".")
    if len(parts) >= 2:
        candidate_id = parts[0].strip()
        col_hint = normalize_name(parts[1].strip())
        return candidate_id, col_hint
        
    return "", ""

def run_file_mapping(
    transformed_tables: Dict[str, Dict], 
    drive_files: List[Dict]
) -> Tuple[Dict[str, List[Dict]], List[Dict], List[Dict]]:
    """
    Khớp các tệp tin từ Drive Catalog vào các bản ghi trong từng bảng.
    Trả về:
      - table_file_maps: Danh sách metadata file được gán theo từng bảng
      - mapped_success: Danh sách file map thành công
      - missing_audit: Danh sách các trường ghi nhận file trên Sheet nhưng không tìm thấy trên Drive
    """
    print(f"[*] Đang thực hiện ánh xạ {len(drive_files)} tệp tin Drive vào các bản ghi...")
    
    # Tạo chỉ mục tìm kiếm nhanh cho drive files
    file_index_by_id = {}
    file_index_by_name = {}
    
    for f in drive_files:
        name = f["file_name"]
        file_index_by_name[name.lower()] = f
        rec_id, _ = extract_id_from_filename(name)
        if rec_id:
            file_index_by_id.setdefault(rec_id.lower(), []).append(f)

    table_file_maps = {}
    mapped_success = []
    missing_audit = []
    
    for sheet_name, table_info in transformed_tables.items():
        df = table_info["dataframe"]
        tbl_name = table_info["table_name"]
        file_candidates = FILE_COLUMNS_MAPPING.get(sheet_name, [])
        norm_file_candidates = [normalize_name(c) for c in file_candidates]
        
        # Tìm xem trong bảng có cột nào khớp với cấu hình file không
        matched_cols = [c for c in df.columns if any(fc in c for fc in norm_file_candidates)]
        
        table_file_maps[sheet_name] = []
        if not matched_cols:
            continue
            
        first_col = df.columns[0] # Khóa chính / ID mặc định
        
        for idx, row in df.iterrows():
            row_id = str(row[first_col]).strip()
            
            for f_col in matched_cols:
                raw_file_val = str(row[f_col]).strip() if pd.notna(row[f_col]) else ""
                if not raw_file_val or raw_file_val.lower() in ["nan", "none", "null", ""]:
                    continue
                
                # 1. Thử tìm theo tên file chính xác
                matched_file = None
                clean_name = raw_file_val.split("/")[-1].strip().lower()
                if clean_name in file_index_by_name:
                    matched_file = file_index_by_name[clean_name]
                    
                # 2. Thử tìm theo ID bản ghi
                if not matched_file and row_id.lower() in file_index_by_id:
                    matched_file = file_index_by_id[row_id.lower()][0]
                    
                if matched_file:
                    entry = {
                        "table_name": tbl_name,
                        "record_id": row_id,
                        "column_name": f_col,
                        "source_file_text": raw_file_val,
                        "drive_file_id": matched_file["drive_file_id"],
                        "file_name": matched_file["file_name"],
                        "file_size_bytes": matched_file["file_size_bytes"],
                        "web_view_link": matched_file["web_view_link"],
                        "download_link": matched_file["download_link"],
                        "status": "MAPPED"
                    }
                    table_file_maps[sheet_name].append(entry)
                    mapped_success.append(entry)
                else:
                    # Ghi nhận file bị thiếu trên Drive
                    missing_entry = {
                        "sheet_name": sheet_name,
                        "record_id": row_id,
                        "column_name": f_col,
                        "expected_file": raw_file_val,
                        "status": "MISSING_ON_DRIVE"
                    }
                    missing_audit.append(missing_entry)
                    
    print(f"[+] Khớp thành công: {len(mapped_success)} tệp tin.")
    if missing_audit:
        print(f"[!] Phát hiện {len(missing_audit)} tệp tin có trên Sheet nhưng thiếu trên Drive.")
        
    return table_file_maps, mapped_success, missing_audit
