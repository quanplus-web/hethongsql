import re
from typing import Dict, List, Tuple
import pandas as pd
from pipeline.table_schema import FILE_COLUMNS_MAPPING, normalize_name

def extract_id_from_filename(filename: str) -> Tuple[str, str]:
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
    print(f"[*] Đang thực hiện ánh xạ {len(drive_files)} tệp tin Drive vào các bản ghi...")
    
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
    used_drive_file_ids = set()
    
    for sheet_name, table_info in transformed_tables.items():
        df = table_info["dataframe"]
        tbl_name = table_info["table_name"]
        file_candidates = FILE_COLUMNS_MAPPING.get(sheet_name, [])
        norm_file_candidates = [normalize_name(c) for c in file_candidates]
        
        matched_cols = [c for c in df.columns if any(fc in c for fc in norm_file_candidates)]
        table_file_maps[sheet_name] = []
        if not matched_cols:
            continue
            
        first_col = df.columns[0]
        
        for idx, row in df.iterrows():
            row_id = str(row[first_col]).strip()
            
            for f_col in matched_cols:
                raw_file_val = str(row[f_col]).strip() if pd.notna(row[f_col]) else ""
                if not raw_file_val or raw_file_val.lower() in ["nan", "none", "null", ""]:
                    # Auto-discovery: If cell is empty, try to find a file by row_id
                    if row_id.lower() in file_index_by_id:
                        matched_file = file_index_by_id[row_id.lower()][0]
                        raw_file_val = "(Auto-discovered)"
                    else:
                        continue
                else:
                    matched_file = None
                    clean_name = raw_file_val.split("/")[-1].strip().lower()
                    if clean_name in file_index_by_name:
                        matched_file = file_index_by_name[clean_name]
                        
                    if not matched_file and row_id.lower() in file_index_by_id:
                        matched_file = file_index_by_id[row_id.lower()][0]
                    
                if matched_file:
                    used_drive_file_ids.add(matched_file["drive_file_id"])
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
                    missing_entry = {
                        "sheet_name": sheet_name,
                        "record_id": row_id,
                        "column_name": f_col,
                        "expected_file": raw_file_val,
                        "status": "MISSING_ON_DRIVE"
                    }
                    missing_audit.append(missing_entry)

    # Thêm danh sách tệp Drive chưa được map (Thừa trên Drive)
    all_drive_audit = list(mapped_success)
    for f in drive_files:
        if f["drive_file_id"] not in used_drive_file_ids:
            all_drive_audit.append({
                "table_name": "N/A (Chưa gán bản ghi)",
                "record_id": f.get("file_name", "").split(".")[0],
                "column_name": "N/A",
                "source_file_text": f["file_name"],
                "drive_file_id": f["drive_file_id"],
                "file_name": f["file_name"],
                "file_size_bytes": f["file_size_bytes"],
                "web_view_link": f["web_view_link"],
                "download_link": f["download_link"],
                "status": "UNMAPPED_EXTRA"
            })
                    
    print(f"[+] Khớp thành công: {len(mapped_success)} lượt map. Tổng số tệp tin Drive: {len(drive_files)}.")
    if missing_audit:
        print(f"[!] Phát hiện {len(missing_audit)} tệp tin có trên Sheet nhưng thiếu trên Drive.")
        
    return table_file_maps, all_drive_audit, missing_audit
