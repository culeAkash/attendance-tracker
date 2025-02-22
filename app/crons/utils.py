from app.databases import postgres_engine,sqlite_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime
import time
import requests
import logging

# Session makers
SQLiteSession = sessionmaker(bind=sqlite_engine)
PostgresSession = sessionmaker(bind=postgres_engine)

# Configure logging
logging.basicConfig(filename="sync-data.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

LAST_RUN_DATA_FILE = Path("last_migration_run.txt")
LAST_RUN_ATTEND_FILE = Path("last_migration_run_attendance.txt")


def get_last_run_time(for_attendance=False):
    """Retrieve the last migration run timestamp from a file."""
    file = LAST_RUN_ATTEND_FILE if for_attendance else LAST_RUN_DATA_FILE
    if file.exists():
        with open(file, "r") as file:
            timestamp = file.read().strip()
            return datetime.fromisoformat(timestamp)
    return None

def set_last_run_time(for_attendance=False):
    """Save the current timestamp as the last migration run time."""
    file1 = LAST_RUN_ATTEND_FILE if for_attendance else LAST_RUN_DATA_FILE
    with open(file1, "w") as file:
        file.write(datetime.now().isoformat())


def check_internet(retries=5, delay=60):
    """Check if the internet is available. Retry 5 times with 1-minute intervals."""
    for attempt in range(1, retries + 1):
        try:
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                logging.info("✅ Internet connection available.")
                return True
        except requests.ConnectionError:
            logging.warning(f"⚠️ No internet. Retry {attempt}/{retries} in {delay} seconds...")
        time.sleep(delay)

    logging.error("❌ No internet after multiple retries. Migration skipped.")
    return False