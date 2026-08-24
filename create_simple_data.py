import sys
import pandas as pd
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

data_dir = Path("data")
data_dir.mkdir(parents=True, exist_ok=True)
mock_drive_dir = data_dir / "mock_drive"
mock_drive_dir.mkdir(parents=True, exist_ok=True)

# Tạo các file mock đính kèm tương ứng
(mock_drive_dir / "00d30875.PROCEDURE FILE.094814.xlsm - Procurement.pdf").write_text("Noi dung file quy trinh Mua Hang (Procurement)", encoding="utf-8")
(mock_drive_dir / "REQ-001.ATTACHMENT.hoa_don_vat_misa.pdf").write_text("Noi dung hoa don VAT phan mem MISA", encoding="utf-8")
(mock_drive_dir / "REQ-003.ATTACHMENT.hop_dong_dich_vu_oracle.pdf").write_text("Noi dung hop dong dich vu Oracle", encoding="utf-8")

file_path = data_dir / "simple_test_data.xlsx"

with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
    # 1. Bảng COMPANY (5 dòng)
    df_company = pd.DataFrame([
        {"COMPANY ID": "COMP-001", "COMPANY NAME": "FPT Software", "TYPE": "Khách hàng", "COUNTRY": "Vietnam", "CITY": "Hanoi"},
        {"COMPANY ID": "COMP-002", "COMPANY NAME": "Viettel Telecom", "TYPE": "Khách hàng", "COUNTRY": "Vietnam", "CITY": "Hanoi"},
        {"COMPANY ID": "COMP-003", "COMPANY NAME": "Vingroup", "TYPE": "Khách hàng", "COUNTRY": "Vietnam", "CITY": "Ho Chi Minh City"},
        {"COMPANY ID": "COMP-004", "COMPANY NAME": "Oracle Corp", "TYPE": "Nhà cung cấp", "COUNTRY": "USA", "CITY": "Austin"},
        {"COMPANY ID": "COMP-005", "COMPANY NAME": "CMC Global", "TYPE": "Đối tác", "COUNTRY": "Vietnam", "CITY": "Da Nang"}
    ])
    df_company.to_excel(writer, sheet_name="COMPANY", index=False)

    # 2. Bảng PROCESS (2 dòng)
    df_process = pd.DataFrame([
        {"PROCESS ID": "00d30875", "PROCESS NAME": "Quy trình Mua hàng", "PROCEDURE FILE": "00d30875.PROCEDURE FILE.094814.xlsm - Procurement.pdf", "PROCEDURE LINK": "https://docs.google.com/procurement"},
        {"PROCESS ID": "242992f0", "PROCESS NAME": "Quy trình Phúc lợi CBNV", "PROCEDURE FILE": None, "PROCEDURE LINK": "https://docs.google.com/welfare"}
    ])
    df_process.to_excel(writer, sheet_name="PROCESS", index=False)

    # 3. Bảng REQUEST (Đã gộp chi tiết & file đính kèm vào chung)
    df_request = pd.DataFrame([
        {
            "REQUEST ID": "REQ-001", 
            "TITLE": "Mua phần mềm kế toán MISA SME", 
            "COMPANY": "COMP-001", 
            "ITEM NAME": "Phần mềm kế toán MISA SME Gói Pro",
            "AMOUNT": 9855000, 
            "CURRENCY": "VND", 
            "ATTACHMENT": "REQ-001.ATTACHMENT.hoa_don_vat_misa.pdf",
            "STATUS": "Approved"
        },
        {
            "REQUEST ID": "REQ-002", 
            "TITLE": "Gói hỗ trợ kỹ thuật MISA", 
            "COMPANY": "COMP-001", 
            "ITEM NAME": "Gói hỗ trợ kỹ thuật bảo trì",
            "AMOUNT": 2000000, 
            "CURRENCY": "VND", 
            "ATTACHMENT": None,
            "STATUS": "Approved"
        },
        {
            "REQUEST ID": "REQ-003", 
            "TITLE": "Gia hạn dịch vụ đám mây Oracle", 
            "COMPANY": "COMP-004", 
            "ITEM NAME": "Oracle Premier Support Renewal",
            "AMOUNT": 5000, 
            "CURRENCY": "USD", 
            "ATTACHMENT": "REQ-003.ATTACHMENT.hop_dong_dich_vu_oracle.pdf",
            "STATUS": "Pending"
        }
    ])
    df_request.to_excel(writer, sheet_name="REQUEST", index=False)

print(f"[+] Đã tạo file Sheet đơn giản (Gộp REQUEST & Detail) tại: {file_path.resolve()}")
