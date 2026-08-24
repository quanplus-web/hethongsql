import os
from pathlib import Path
from typing import Dict, List
import config
from pipeline.table_schema import (
    TABLE_DEPENDENCY_ORDER, 
    MASTER_DATA_SHEETS, 
    TRANSACTION_SHEETS, 
    normalize_name
)

def build_create_table_sql(table_name: str, columns: List[str]) -> str:
    col_defs = []
    for i, col in enumerate(columns):
        if i == 0:
            col_defs.append(f'    "{col}" VARCHAR(255) PRIMARY KEY')
        else:
            col_defs.append(f'    "{col}" TEXT')
            
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    sql += ",\n".join(col_defs)
    sql += "\n);\n"
    return sql

def build_insert_statements(table_name: str, columns: List[str], rows: List[List[str]], chunk_size=500) -> str:
    if not rows:
        return ""
        
    cols_str = ", ".join([f'"{c}"' for c in columns])
    lines = []
    
    # Chia nhỏ dữ liệu thành các cục (chunk), mỗi cục 500 dòng để không bị quá tải
    for i in range(0, len(rows), chunk_size):
        chunk_rows = rows[i:i + chunk_size]
        values_list = []
        
        for r in chunk_rows:
            vals_str = ", ".join(r)
            values_list.append(f"  ({vals_str})")
            
        # Gộp thành 1 lệnh Bulk Insert
        bulk_insert = f"INSERT INTO {table_name} ({cols_str}) VALUES\n" + ",\n".join(values_list) + ";"
        lines.append(bulk_insert)
        
    return "\n\n".join(lines) + "\n"

def build_files_table_sql(mapped_files: List[Dict]) -> str:
    sql = """-- ==============================================================================
-- BẢNG LƯU TRỮ METADATA VÀ FILE NHỊ PHÂN (BLOB)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS file_attachments (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    column_name VARCHAR(100),
    file_name TEXT,
    file_size_bytes BIGINT,
    file_data BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);\n\n"""
    
    mock_dir = Path(config.MOCK_DRIVE_DIR)
    
    if mapped_files:
        for f in mapped_files:
            tbl = f["table_name"]
            rec_id = f["record_id"].replace("'", "''")
            col = f["column_name"]
            fname = f["file_name"].replace("'", "''")
            fsize = f["file_size_bytes"]
            
            # Đọc file vật lý và chuyển thành chuỗi Hex
            file_path = mock_dir / f["file_name"]
            file_hex_str = "NULL"
            
            if file_path.exists() and file_path.is_file():
                try:
                    with open(file_path, "rb") as bin_file:
                        binary_data = bin_file.read()
                        # Chuyển nhị phân thành chuỗi Hex \x... cho PostgreSQL
                        hex_data = binary_data.hex()
                        file_hex_str = f"'\\x{hex_data}'"
                except Exception as e:
                    print(f"[!] Lỗi đọc file {fname}: {e}")
            else:
                print(f"[!] Không tìm thấy file vật lý {fname} trong {mock_dir}")
                
            sql += f"INSERT INTO file_attachments (table_name, record_id, column_name, file_name, file_size_bytes, file_data) VALUES ('{tbl}', '{rec_id}', '{col}', '{fname}', {fsize}, {file_hex_str});\n"
            
    return sql

def run_generate_sql(
    transformed_tables: Dict[str, Dict], 
    mapped_files: List[Dict]
) -> Dict[str, str]:
    print("[*] Đang sinh các tập lệnh SQL (.sql) theo thứ tự phụ thuộc bảng...")
    out_dir = Path(config.OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    ordered_sheets = []
    individual_files = []
    for s in TABLE_DEPENDENCY_ORDER:
        if s in transformed_tables:
            ordered_sheets.append(s)
            
    for s in transformed_tables:
        if s not in ordered_sheets:
            ordered_sheets.append(s)

    master_sql_parts = ["-- ==============================================================================\n-- 01. MASTER DATA & DANH MỤC CƠ BẢN\n-- ==============================================================================\nBEGIN;\n"]
    transaction_sql_parts = ["-- ==============================================================================\n-- 02. TRANSACTION DATA & BẢNG NGHIỆP VỤ\n-- ==============================================================================\nBEGIN;\n"]
    all_sql_parts = ["-- ==============================================================================\n-- TOÀN BỘ KỊCH BẢN MIGRATION DỮ LIỆU TỰ ĐỘNG\n-- ==============================================================================\nBEGIN;\n"]
    
    for sheet in ordered_sheets:
        info = transformed_tables[sheet]
        tbl = info["table_name"]
        cols = info["columns"]
        rows = info["rows"]
        
        create_sql = build_create_table_sql(tbl, cols)
        insert_sql = build_insert_statements(tbl, cols, rows)
        chunk = f"\n-- BẢNG: {sheet} -> {tbl} ({len(rows)} bản ghi)\n" + create_sql + insert_sql
        
        p_tbl = out_dir / f"{tbl}.sql"
        with open(p_tbl, "w", encoding="utf-8") as f:
            f.write(f"-- ==============================================================================\n-- BẢNG: {sheet}\n-- ==============================================================================\nBEGIN;\n")
            f.write(chunk)
            f.write("\nCOMMIT;\n")
            
        individual_files.append({"table": tbl, "sheet": sheet, "path": str(p_tbl), "filename": f"{tbl}.sql", "records": len(rows)})
        
        all_sql_parts.append(chunk)
        if sheet in MASTER_DATA_SHEETS:
            master_sql_parts.append(chunk)
        else:
            transaction_sql_parts.append(chunk)
            
    master_sql_parts.append("\nCOMMIT;\n")
    transaction_sql_parts.append("\nCOMMIT;\n")
    
    files_sql = build_files_table_sql(mapped_files)
    all_sql_parts.append("\n" + files_sql + "\nCOMMIT;\n")
    
    p_master = out_dir / "01_master_data.sql"
    p_trans = out_dir / "02_transaction_data.sql"
    p_files = out_dir / "03_files_data.sql"
    p_all = out_dir / "all_migration.sql"
    
    with open(p_master, "w", encoding="utf-8") as f:
        f.write("".join(master_sql_parts))
    with open(p_trans, "w", encoding="utf-8") as f:
        f.write("".join(transaction_sql_parts))
    with open(p_files, "w", encoding="utf-8") as f:
        f.write(files_sql)
    with open(p_all, "w", encoding="utf-8") as f:
        f.write("".join(all_sql_parts))
        
    print(f"[+] Đã xuất thành công các file SQL:")
    print(f"    - {p_master.name}")
    print(f"    - {p_trans.name}")
    print(f"    - {p_files.name}")
    print(f"    - {p_all.name}")
    
    return {
        "master_sql": str(p_master),
        "transaction_sql": str(p_trans),
        "files_sql": str(p_files),
        "all_sql": str(p_all),
        "individual_files": individual_files
    }
