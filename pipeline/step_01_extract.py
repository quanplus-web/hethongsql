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
        df = df.dropna(how="all").dropna(axis=1, how="all")
        tables_data[sheet] = df
        print(f"    - [{sheet}]: {len(df)} dòng, {len(df.columns)} cột")
        
    return tables_data

def scan_drive_catalog(drive_folder_id: str = None) -> List[Dict]:
    """
    Quét danh mục tệp tin từ Google Drive online hoặc thư mục Mock Drive cục bộ.
    Nếu người dùng chủ động điền Drive Folder ID mà thiếu file credentials.json hoặc ID lỗi -> Báo lỗi chính xác.
    """
    folder_id = drive_folder_id or config.GOOGLE_DRIVE_FOLDER_ID
    files_catalog = []
    
    # Nếu người dùng có nhập Folder ID trên Google Drive
    if folder_id and str(folder_id).strip():
        folder_id = str(folder_id).strip()
        creds_path = config.GOOGLE_SERVICE_ACCOUNT_JSON
        
        if not os.path.exists(creds_path):
            raise FileNotFoundError(
                f"Để quét trực tuyến Folder ID '{folder_id}' từ Google Drive, bạn cần có file 'credentials.json' (Google Service Account) trong thư mục d:\\toolsql. Nếu muốn test cục bộ, hãy xóa ID trong ô nhập."
            )
            
        try:
            print(f"[*] Đang kết nối Google Drive API (Folder ID: {folder_id})...")
            from googleapiclient.discovery import build
            from google.oauth2 import service_account
            
            creds = service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            service = build('drive', 'v3', credentials=creds)
            query = f"'{folder_id}' in parents and trashed = false"
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
            raise ValueError(f"Không thể kết nối Google Drive với Folder ID '{folder_id}'. Lỗi: {e}")

    # Chế độ Fallback Mock Drive cục bộ khi không điền ID
    mock_dir = Path(config.MOCK_DRIVE_DIR)
    if mock_dir.exists():
        print(f"[*] Đang quét thư mục Mock Drive cục bộ: {mock_dir.resolve()}...")
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

def run_extract(excel_path: str = None, drive_folder_id: str = None) -> Tuple[Dict[str, pd.DataFrame], List[Dict]]:
    path = excel_path or config.EXCEL_FILE_PATH
    tables = extract_excel_sheets(path)
    drive_files = scan_drive_catalog(drive_folder_id=drive_folder_id)
    return tables, drive_files
