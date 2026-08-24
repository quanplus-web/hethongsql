import re

def normalize_name(name: str) -> str:
    """Chuyển đổi tên Sheet/Cột từ Excel sang định dạng SQL snake_case an toàn."""
    if not name:
        return "col"
    s = str(name).strip().lower()
    s = re.sub(r'[\s\-/\.]+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    s = re.sub(r'_+', '_', s).strip('_')
    if not s or s[0].isdigit():
        s = f"c_{s}"
    return s

# Thứ tự bảng phụ thuộc (Dependency Order) để INSERT không bị lỗi Foreign Keys
TABLE_DEPENDENCY_ORDER = [
    # 1. Bảng độc lập / Master lookup
    "COUNTRY AND CITY",
    "MY COMPANY",
    "MY LOCATION",
    "DEPARTMENT",
    "EMPLOYEE",
    "COMPANY",
    "CONTACT",
    "ACCOUNT",
    "MTR",
    "ASSET CATEGORY",
    "OPERATION PROGRAM",
    "REEX",
    "MY SERVICE",
    "PROCESS",
    
    # 2. Bảng nghiệp vụ trung gian / Cha
    "REQUEST",
    "OPPORTUNITIES",
    "PAL",
    "ASSETS",
    "ASSET",
    "SERVICE",
    
    # 3. Bảng chi tiết / Giao dịch con (Transactions & Attachments)
    "REQUEST DETAIL",
    "ORDERS",
    "INVOICE",
    "PAYMENT",
    "EXPENSE",
    "FINANCE",
    "ASSET TRANSACTION",
    "SERVICE ORDER",
    "SERVICE REQUEST",
    "PAL SERVICE",
]

# Phân nhóm để xuất file SQL riêng biệt theo yêu cầu của Sếp
MASTER_DATA_SHEETS = [
    "COUNTRY AND CITY", "MY COMPANY", "MY LOCATION", "DEPARTMENT", "EMPLOYEE",
    "COMPANY", "CONTACT", "ACCOUNT", "MTR", "ASSET CATEGORY", "OPERATION PROGRAM",
    "REEX", "MY SERVICE", "PROCESS"
]

TRANSACTION_SHEETS = [
    "REQUEST", "OPPORTUNITIES", "PAL", "ASSETS", "ASSET", "SERVICE",
    "REQUEST DETAIL", "ORDERS", "INVOICE", "PAYMENT", "EXPENSE", "FINANCE",
    "ASSET TRANSACTION", "SERVICE ORDER", "SERVICE REQUEST", "PAL SERVICE"
]

# Các cột chứa File / Tệp đính kèm cần quét và khớp với Google Drive
FILE_COLUMNS_MAPPING = {
    "PROCESS": ["PROCEDURE FILE", "PROCEDURE LINK"],
    "REQUEST": ["ATTACHMENT", "FILE", "FILE NAME", "ATTACHMENT FILE", "FILE ATTACHMENT"],
    "REQUEST DETAIL": ["ATTACHMENT", "FILE", "FILE NAME", "ATTACHMENT FILE", "FILE ATTACHMENT"],
    "INVOICE": ["INVOICE FILE", "FILE", "ATTACHMENT", "INVOICE LINK"],
    "PAYMENT": ["PAYMENT FILE", "UNC FILE", "FILE", "ATTACHMENT", "PAYMENT PROOF"],
    "EXPENSE": ["RECEIPT FILE", "FILE", "ATTACHMENT"],
    "ASSET": ["HANDOVER FILE", "FILE", "ATTACHMENT"],
    "SERVICE ORDER": ["CONTRACT FILE", "ATTACHMENT", "FILE"],
}
