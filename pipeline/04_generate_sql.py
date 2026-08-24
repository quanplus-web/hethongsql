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
    """Tạo câu lệnh CREATE TABLE an toàn."""
    col_defs = []
    for i, col in enumerate(columns):
        if i == 0:
            # Cột đầu tiên coi như ID/Khóa chính
            col_defs.append(f"    {col} VARCHAR(255) PRIMARY KEY")
        else:
            col_defs.append(f"    {col} TEXT")
            
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    sql += ",\n".join(col_defs)
    sql += "\n);\n"
    return sql

def build_insert_statements(table_name: str, columns: List[str], rows: List[List[str]]) -> str:
    """Tạo danh sách các câu lệnh INSERT INTO."""
    if not rows:
        return ""
        
    cols_str = ", ".join(columns)
    lines = []
    for r in rows:
        vals_str = ", ".join(r)
        lines.append(f"INSERT INTO {table_name} ({cols_str}) VALUES ({vals_str});")
        
    return "\n".join(lines) + "\n"

def build_files_table_sql(mapped_files: List[Dict]) -> str:
    """Tạo bảng lưu trữ metadata file và câu lệnh INSERT file."""
    sql = """-- ==============================================================================
-- BẢNG LƯU TRỮ METADATA TỆP TIN GOOGLE DRIVE (FILE ATTACHMENTS)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS file_attachments (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    column_name VARCHAR(100),
    file_name TEXT,
    drive_file_id VARCHAR(100),
    file_size_bytes BIGINT,
    web_view_link TEXT,
    download_link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);\n\n"""
    
    if mapped_files:
        for f in mapped_files:
            tbl = f["table_name"]
            rec_id = f["record_id"].replace("'", "''")
            col = f["column_name"]
            fname = f["file_name"].replace("'", "''")
            fid = f["drive_file_id"]
            fsize = f["file_size_bytes"]
            wv_link = f["web_view_link"].replace("'", "''")
            dl_link = f["download_link"].replace("'", "''")
            
            sql += f"INSERT INTO file_attachments (table_name, record_id, column_name, file_name, drive_file_id, file_size_bytes, web_view_link, download_link) VALUES ('{tbl}', '{rec_id}', '{col}', '{fname}', '{fid}', {fsize}, '{wv_link}', '{dl_link}');\n"
            
    return sql

def run_generate_sql(
    transformed_tables: Dict[str, Dict], 
    mapped_files: List[Dict]
) -> Dict[str, str]:
    """
    Sinh toàn bộ các file .sql theo đúng thứ tự phụ thuộc và lưu vào thư mục output/.
    """
    print("[*] Đang sinh các tập lệnh SQL (.sql) theo thứ tự phụ thuộc bảng...")
    out_dir = Path(config.OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Sắp xếp các sheet theo thứ tự dependency
    ordered_sheets = []
    for s in TABLE_DEPENDENCY_ORDER:
        if s in transformed_tables:
            ordered_sheets.append(s)
            
    # Thêm các sheet còn lại nếu chưa nằm trong TABLE_DEPENDENCY_ORDER
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
        
        all_sql_parts.append(chunk)
        if sheet in MASTER_DATA_SHEETS:
            master_sql_parts.append(chunk)
        else:
            transaction_sql_parts.append(chunk)
            
    master_sql_parts.append("\nCOMMIT;\n")
    transaction_sql_parts.append("\nCOMMIT;\n")
    
    # Tạo phần file SQL
    files_sql = build_files_table_sql(mapped_files)
    all_sql_parts.append("\n" + files_sql + "\nCOMMIT;\n")
    
    # Lưu các file ra đĩa
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
        "all_sql": str(p_all)
    }
