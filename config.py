import os
from pathlib import Path
from dotenv import load_dotenv

# Tải cấu hình từ .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

EXCEL_FILE_PATH = os.getenv("EXCEL_FILE_PATH", "data/RQC-CP-Database.xlsx")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "").strip()
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
MOCK_DRIVE_DIR = os.getenv("MOCK_DRIVE_DIR", "data/mock_drive")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "credentials.json")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
DB_DIALECT = os.getenv("DB_DIALECT", "postgres").lower()

# Đảm bảo các thư mục tồn tại
Path(BASE_DIR / OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
Path(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)
Path(BASE_DIR / MOCK_DRIVE_DIR).mkdir(parents=True, exist_ok=True)
