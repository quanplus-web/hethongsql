import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import config

def extract_excel_sheets(excel_path: str) -> Dict[str, pd.DataFrame]:
    """Đọc toàn bộ các sheets từ file Excel nguồn."""
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Không tìm thấy file Excel tại: {excel_path}")
    
    print(f"[*] Đang đọc file Excel: {excel_path}...")
    xls = pd.ExcelFile(excel_path, engine="openpyxl")
    sheet_names = xls.sheet_names
    print(f"[+] Tìm thấy {len(sheet_names)} sheets: {', '.join(sheet_names[:6])}...")
    
    tables_data = {}
    for sheet in sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet)
        # Loại bỏ các cột hoặc dòng hoàn toàn rỗng
        df = df.dropna(how="all").dropna(axis=1, how="all")
        tables_data[sheet] = df
        print(f"    - [{sheet}]: {len(df)} dòng, {len(df.columns)} cột")
        
    return tables_data

def scan_drive_catalog() -> List[Dict]:
    """
    Quét danh mục tệp tin từ Google Drive hoặc thư mục Mock Drive cục bộ.
    Cho phép nhân viên tự kiểm thử mà không cần đợi sếp share quyền.
    """
    files_catalog = []
    
    # 1. Thử kết nối Google Drive API nếu có cấu hình Folder ID và Credentials
    if config.GOOGLE_DRIVE_FOLDER_ID and os.path.exists(config.GOOGLE_SERVICE_ACCOUNT_JSON):
        try:
            print(f"[*] Đang kết nối Google Drive API (Folder: {config.GOOGLE_DRIVE_FOLDER_ID})...")
            from googleapiclient.discovery import build
            from google.oauth2 import service_account
            
            creds = service_account.Credentials.from_service_account_file(
                config.GOOGLE_SERVICE_ACCOUNT_JSON,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            service = build('drive', 'v3', credentials=creds)
            query = f"'{config.GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed = false"
            results = service.files().list(
                q=query,
                pageSize=1000,
                fields="files(id, name, size, mimeType, webViewLink, md5Checksum, modifiedTime)"
            ).execute()
            
            items = results.get('files', [])
            for item in items:
                files_catalog.append({
                    "drive_file_id": item.get("id"),
                    "file_name": item.get("name"),
                    "file_size_bytes": int(item.get("size", 0)),
                    "mime_type": item.get("mimeType"),
                    "web_view_link": item.get("webViewLink"),
                    "download_link": f"https://drive.google.com/uc?export=download&id={item.get('id')}",
                    "md5_checksum": item.get("md5Checksum"),
                    "source": "google_drive"
                })
            print(f"[+] Đã quét thành công {len(files_catalog)} tệp tin từ Google Drive.")
            return files_catalog
        except Exception as e:
            print(f"[!] Không thể quét qua Google Drive API ({e}). Chuyển sang quét Mock Drive cục bộ.")

    # 2. Quét thư mục Mock Drive cục bộ (Testing Mode)
    mock_dir = Path(config.MOCK_DRIVE_DIR)
    if mock_dir.exists():
        print(f"[*] Đang quét thư mục Mock Drive: {mock_dir.resolve()}...")
        for p in mock_dir.rglob("*"):
            if p.is_file():
                stat = p.stat()
                file_id = f"mock_{abs(hash(p.name)) % 100000000}"
                files_catalog.append({
                    "drive_file_id": file_id,
                    "file_name": p.name,
                    "file_size_bytes": stat.st_size,
                    "mime_type": "application/octet-stream",
                    "web_view_link": f"https://drive.google.com/file/d/{file_id}/view",
                    "download_link": f"https://drive.google.com/uc?export=download&id={file_id}",
                    "md5_checksum": "mock_checksum",
                    "source": "mock_local"
                })
        print(f"[+] Tìm thấy {len(files_catalog)} tệp tin trong Mock Drive.")
        
    return files_catalog

def run_extract(excel_path: str = None) -> Tuple[Dict[str, pd.DataFrame], List[Dict]]:
    """Chạy toàn bộ giai đoạn Extract."""
    path = excel_path or config.EXCEL_FILE_PATH
    tables = extract_excel_sheets(path)
    drive_files = scan_drive_catalog()
    return tables, drive_files

if __name__ == "__main__":
    tables, files = run_extract()
    print("\n[V] Hoàn tất trích xuất dữ liệu.")
