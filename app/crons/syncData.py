from fastapi_utils.tasks import repeat_every
from fastapi import Depends
import logging
import time
import requests
from app.models import Student,Staff,Parent,Address,Standard,GovtId,Attendance
from app.databases import postgres_engine,sqlite_engine
from sqlalchemy import insert,select
from sqlalchemy.orm import Session,sessionmaker
# Configure logging
logging.basicConfig(filename="sync.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Session makers
SQLiteSession = sessionmaker(bind=sqlite_engine)
PostgresSession = sessionmaker(bind=postgres_engine)

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

def migrate_staff_data():
    """Migrate data for a specific table using SQLAlchemy."""
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    logging.info("Migrating staff data...")
    logging.info("Migrating remote data...")
    try:
        staff_data = sqlite_session.query(Staff).filter(Staff.is_synced==False).all()
        if len(staff_data) == 0:
            logging.info(f"⚠️ No data to migrate for table: Staff")
            return True  # Continue with the next table
        
        
        for row in staff_data:
            # row.__delattr__("_sa_instance_state")
            row.__setattr__("is_synced", True)
            
        data_dicts = [row.__dict__ for row in staff_data]
        
        postgres_session.bulk_insert_mappings(Staff, data_dicts)
        postgres_session.flush()
        
        # update staff table in local db updating is_synced  == True
        sqlite_session.query(Staff).filter(Staff.is_synced==False).update({"is_synced":True})
        sqlite_session.commit()
        postgres_session.commit()
        logging.info(f"✅ Data migrated for table: Staff")
        return True
    except Exception as e:
        sqlite_session.rollback()
        postgres_session.rollback()
        logging.error(f"❌ Error migrating Staff Table: {str(e)}")
        return False
    finally:
        sqlite_session.close()
        postgres_session.close()
    


@repeat_every(seconds=60*60*24*30)
async def migrate_data():
    logging.info("🔄 Scheduled migration started...")
    
    if check_internet():
        logging.info("🌍 Internet connected! Starting migration...")
        tables = [
            ("Staff",Staff),
            # ("Standard",Standard),
            # ("Parent",Parent),
            # ("Address",Address),
            # ("Student",Student),
            # ("GovtId",GovtId)
        ]
        # for table_name, model in tables:
        failed_tables = []
        success = migrate_staff_data()
        if not success:
            failed_tables.append("Staff")
        
        if failed_tables:
            logging.error(f"❌ Migration failed for tables: {', '.join(failed_tables)}")
        else:
            logging.info("✅ Migration completed successfully.")
    else:
        logging.error("❌ Migration failed due to no internet.")