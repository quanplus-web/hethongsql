import os
import sys
import argparse
from pathlib import Path

# Đảm bảo mã hóa UTF-8 cho console Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import config
from pipeline.step_01_extract import run_extract
from pipeline.step_02_transform import run_transform
from pipeline.step_03_file_mapping import run_file_mapping
from pipeline.step_04_generate_sql import run_generate_sql
from pipeline.step_05_validate import run_validation

def create_sample_mock_data_if_missing():
    """Tạo dữ liệu mẫu 30 sheets nếu chưa có file Excel để nhân viên test ngay lập tức."""
    excel_path = Path(config.EXCEL_FILE_PATH)
    if not excel_path.exists():
        print(f"[*] Chưa phát hiện file {config.EXCEL_FILE_PATH}, đang tự động khởi tạo dữ liệu mẫu 30 sheets để kiểm thử...")
        import pandas as pd
        
        mock_dir = Path(config.MOCK_DRIVE_DIR)
        mock_dir.mkdir(parents=True, exist_ok=True)
        
        # Tạo file Drive mẫu
        sample_file_1 = mock_dir / "00d30875.PROCEDURE FILE.094814.xlsm - Procurement.pdf"
        sample_file_2 = mock_dir / "REQ-001.ATTACHMENT.invoice_vat.pdf"
        sample_file_1.write_text("Mock PDF content for Procurement", encoding="utf-8")
        sample_file_2.write_text("Mock PDF content for Invoice VAT", encoding="utf-8")
        
        # Tạo 30 sheets mẫu
        writer = pd.ExcelWriter(excel_path, engine="openpyxl")
        
        from pipeline.table_schema import TABLE_DEPENDENCY_ORDER
        for sheet_name in TABLE_DEPENDENCY_ORDER:
            if sheet_name == "COMPANY":
                df = pd.DataFrame([
                    {"COMPANY ID": "COMP-001", "COMPANY NAME": "FPT Software", "TYPE": "Khách hàng", "COUNTRY": "Vietnam", "CITY": "Hanoi"},
                    {"COMPANY ID": "COMP-002", "COMPANY NAME": "Viettel Group", "TYPE": "Khách hàng", "COUNTRY": "Vietnam", "CITY": "Hanoi"},
                    {"COMPANY ID": "COMP-003", "COMPANY NAME": "Vingroup", "TYPE": "Khách hàng", "COUNTRY": "Vietnam", "CITY": "Ho Chi Minh City"},
                    {"COMPANY ID": "COMP-004", "COMPANY NAME": "Oracle Vietnam", "TYPE": "Nhà cung cấp", "COUNTRY": "USA", "CITY": "Austin"},
                    {"COMPANY ID": "COMP-005", "COMPANY NAME": "Redhat Inc", "TYPE": "Nhà cung cấp", "COUNTRY": "USA", "CITY": "Raleigh"},
                    {"COMPANY ID": "COMP-006", "COMPANY NAME": "CMC Telecom", "TYPE": "Đối tác", "COUNTRY": "Vietnam", "CITY": "Da Nang"},
                ])
            elif sheet_name == "PROCESS":
                df = pd.DataFrame([
                    {"PROCESS ID": "00d30875", "PROCESS NAME": "Procurement Process", "PROCEDURE FILE": "00d30875.PROCEDURE FILE.094814.xlsm - Procurement.pdf", "PROCEDURE LINK": "https://docs.google.com/procurement"},
                    {"PROCESS ID": "242992f0", "PROCESS NAME": "Welfare Process", "PROCEDURE FILE": None, "PROCEDURE LINK": "https://docs.google.com/welfare"}
                ])
            elif sheet_name == "REQUEST DETAIL":
                df = pd.DataFrame([
                    {"DETAIL ID": "RD-001", "REQUEST ID": "REQ-001", "ITEM NAME": "Oracle Premier Support", "AMOUNT": 9855000, "CURRENCY": "VND", "ATTACHMENT": "REQ-001.ATTACHMENT.invoice_vat.pdf"},
                    {"DETAIL ID": "RD-002", "REQUEST ID": "REQ-001", "ITEM NAME": "GSuite Starter Package", "AMOUNT": 4955940, "CURRENCY": "VND", "ATTACHMENT": None}
                ])
            else:
                df = pd.DataFrame([
                    {"ID": f"{sheet_name[:3]}-001", "NAME": f"Sample {sheet_name} 1", "STATUS": "ACTIVE", "CREATED_DATE": "2024-09-01"},
                    {"ID": f"{sheet_name[:3]}-002", "NAME": f"Sample {sheet_name} 2", "STATUS": "ACTIVE", "CREATED_DATE": "2024-09-02"}
                ])
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
        writer.close()
        print(f"[+] Đã tạo file Excel mẫu 30 sheets tại: {excel_path.resolve()}")

def main():
    parser = argparse.ArgumentParser(description="Tool Migration Dữ Liệu Excel/Sheets & Drive sang SQL")
    parser.add_argument("--excel-path", help="Đường dẫn file Excel nguồn", default=None)
    args = parser.parse_args()

    print("=" * 70)
    print("      AUTOMATED DATA MIGRATION & DRIVE FILE MAPPING TOOL")
    print("=" * 70)
    
    # 0. Đảm bảo có dữ liệu test
    create_sample_mock_data_if_missing()
    
    # 1. Trích xuất (Extract)
    print("\n>>> GIAI ĐOẠN 1: EXTRACT DATA & DRIVE CATALOG")
    tables_data, drive_files = run_extract(args.excel_path)
    
    # 2. Chuẩn hóa (Transform)
    print("\n>>> GIAI ĐOẠN 2: TRANSFORM & CLEANING")
    transformed_tables = run_transform(tables_data)
    
    # 3. Khớp tệp tin Drive (File Mapping)
    print("\n>>> GIAI ĐOẠN 3: GOOGLE DRIVE FILE MAPPING")
    table_files, mapped_success, missing_audit = run_file_mapping(transformed_tables, drive_files)
    
    # 4. Sinh mã SQL (SQL Generation)
    print("\n>>> GIAI ĐOẠN 4: SQL GENERATOR (SAFE TRANSACTION)")
    sql_outputs = run_generate_sql(transformed_tables, mapped_success)
    
    # 5. Đối soát (Validation)
    print("\n>>> GIAI ĐOẠN 5: VALIDATION MATRIX & REPORTS")
    val_outputs = run_validation(transformed_tables, mapped_success, missing_audit)
    
    print("\n" + "=" * 70)
    print("                     KẾT QUẢ HOÀN THÀNH")
    print("=" * 70)
    print(f"[V] File SQL toàn bộ:      {sql_outputs['all_sql']}")
    print(f"[V] File SQL Master Data:   {sql_outputs['master_sql']}")
    print(f"[V] File SQL Transactions:  {sql_outputs['transaction_sql']}")
    print(f"[V] File SQL Tệp đính kèm:  {sql_outputs['files_sql']}")
    print(f"[V] Báo cáo Đối Soát Excel: {val_outputs['report_excel']}")
    print(f"[V] Báo cáo Đối Soát MD:    {val_outputs['report_md']}")
    print("=" * 70)
    print("(*) Lưu ý: Các file .sql đã sẵn sàng trong thư mục output/ để gửi Sếp duyệt trước khi nạp DB.")

if __name__ == "__main__":
    main()
