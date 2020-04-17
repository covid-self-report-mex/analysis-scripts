import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

current_dir = Path(__file__).parent.absolute()
project_dir = current_dir / '..'
env_path = current_dir / '..' / '.env'
load_dotenv(dotenv_path=env_path, verbose=True)

READ_TOKEN = os.getenv("READ_TOKEN")
READ_API_URL = os.getenv("READ_API_URL")

DATABASE = os.getenv("DATABASE_NAME")
MYSQL_PORT = os.getenv("MYSQL_PORT")
GEOCODING_RAW_FILE_URL = os.getenv("GEOCODING_RAW_FILE_URL")


OUTPUT_DATASETS_PATH = project_dir / 'output_datasets'
TMP_PATH = project_dir / 'tmp'
BACKUP_PATH = project_dir / 'backups'
BACKUP_DOCUMENTS_PATH = BACKUP_PATH / 'documents'

# outputs
DAILY_REPORT_DIR = OUTPUT_DATASETS_PATH / 'daily-reports'

if not OUTPUT_DATASETS_PATH.exists():
    OUTPUT_DATASETS_PATH.mkdir()

if not BACKUP_PATH.exists():
    BACKUP_PATH.mkdir()

if not BACKUP_DOCUMENTS_PATH.exists():
    BACKUP_DOCUMENTS_PATH.mkdir()

if not DAILY_REPORT_DIR.exists():
    DAILY_REPORT_DIR.mkdir()

if not TMP_PATH.exists():
    TMP_PATH.mkdir()
