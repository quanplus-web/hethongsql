import re
import datetime
from typing import Dict, Any, List, Tuple
import pandas as pd
from pipeline.table_schema import normalize_name

def escape_sql_val(val: Any) -> str:
    if val is None or pd.isna(val):
        return "NULL"
    
    if isinstance(val, (int,)):
        return str(val)
    
    if isinstance(val, (float,)):
        if pd.isna(val):
            return "NULL"
        if val.is_integer():
            return str(int(val))
        return f"{val:.4f}".rstrip('0').rstrip('.')
    
    if isinstance(val, (datetime.datetime, datetime.date)):
        return f"'{val.strftime('%Y-%m-%d %H:%M:%S')}'"
    
    if isinstance(val, bool):
        return "TRUE" if val else "FALSE"
        
    s = str(val).strip()
    if s == "" or s.lower() == "nan" or s.lower() == "none" or s.lower() == "null":
        return "NULL"
        
    s = s.replace("'", "''")
    return f"'{s}'"

def transform_dataframe(sheet_name: str, df: pd.DataFrame) -> Tuple[List[str], List[List[str]], pd.DataFrame]:
    cleaned_df = df.copy()
    cleaned_df.dropna(how="all", inplace=True) # Xóa các dòng trống hoàn toàn
    
    raw_columns = list(cleaned_df.columns)
    sql_columns = []
    seen_cols = set()
    
    for c in raw_columns:
        norm = normalize_name(str(c))
        original_norm = norm
        count = 1
        while norm in seen_cols:
            norm = f"{original_norm}_{count}"
            count += 1
        seen_cols.add(norm)
        sql_columns.append(norm)
        
    cleaned_df.columns = sql_columns
    
    sql_rows = []
    for _, row in cleaned_df.iterrows():
        row_vals = [escape_sql_val(row[col]) for col in sql_columns]
        sql_rows.append(row_vals)
        
    return sql_columns, sql_rows, cleaned_df

def run_transform(tables_data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
    transformed = {}
    print("[*] Đang làm sạch và chuẩn hóa kiểu dữ liệu cho các bảng...")
    
    for sheet_name, df in tables_data.items():
        sql_cols, sql_rows, cleaned_df = transform_dataframe(sheet_name, df)
        table_name = normalize_name(sheet_name)
        transformed[sheet_name] = {
            "table_name": table_name,
            "columns": sql_cols,
            "rows": sql_rows,
            "dataframe": cleaned_df,
            "total_rows": len(cleaned_df)
        }
        
    print(f"[+] Hoàn tất làm sạch {len(transformed)} bảng.")
    return transformed
