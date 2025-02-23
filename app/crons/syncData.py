from fastapi_utils.tasks import repeat_every
import logging
from app.models import Student,Staff,Parent,Address,Standard,GovtId,UserType,GovtIdTypes
from datetime import datetime, timedelta
from .utils import get_last_run_time,set_last_run_time,SQLiteSession,PostgresSession,check_internet

# Configure logging
logging.basicConfig(filename="sync-data.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# migrate staff data


def migrate_staff_data():
    """Migrate data for a specific table using SQLAlchemy."""
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    logging.info("Migrating staff data...")
    # logging.info("Migrating remote data...")
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
        
# migrate Standard Data
def migrate_standard_data():
    """Migrate data for a specific table using SQLAlchemy."""
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    logging.info("Migrating Standard data...")
    try:
        standard_data = sqlite_session.query(Standard).filter(Standard.is_synced==False).all()
        if len(standard_data) == 0:
            logging.info(f"⚠️ No data to migrate for table: Standard")
            return True  # Continue with the next table
        
        
        data_dicts = []
        for row in standard_data:
            # check for each standard if corresponding Staff exists in cloud table
            staff = postgres_session.query(Staff).filter(Staff.staff_id==row.class_teacher_id).first()
            if not staff:
                # skip this standard
                continue
            # update staff table in local db updating is_synced  == True
            sqlite_session.query(Standard).filter(Standard.standard_id==row.standard_id).update({"is_synced":True})
            row.__setattr__("is_synced", True)
            data_dicts.append(row.__dict__)
        
        # store the standards which have their teacher id present to the cloud table
        postgres_session.bulk_insert_mappings(Standard, data_dicts)
        postgres_session.flush()
        
        # commit the changes
        sqlite_session.commit()
        postgres_session.commit()
        logging.info(f"✅ Data migrated for table: Staff")
        return True
    except Exception as e:
        sqlite_session.rollback()
        postgres_session.rollback()
        logging.error(f"❌ Error migrating Standard Table: {str(e)}")
        return False
    finally:
        sqlite_session.close()
        postgres_session.close()

# migrate parent data
def migrate_parent_data():
    """Migrate data for a specific table using SQLAlchemy."""
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    logging.info("Migrating Parent data...")
    # logging.info("Migrating remote data...")
    try:
        parent_data = sqlite_session.query(Parent).filter(Parent.is_synced==False).all()
        if len(parent_data) == 0:
            logging.info(f"⚠️ No data to migrate for table: Parent")
            return True  # Continue with the next table
        
        
        for row in parent_data:
            # row.__delattr__("_sa_instance_state")
            row.__setattr__("is_synced", True)
            
        data_dicts = [row.__dict__ for row in parent_data]
        
        postgres_session.bulk_insert_mappings(Parent, data_dicts)
        postgres_session.flush()
        
        # update staff table in local db updating is_synced  == True
        sqlite_session.query(Parent).filter(Parent.is_synced==False).update({"is_synced":True})
        sqlite_session.commit()
        postgres_session.commit()
        logging.info(f"✅ Data migrated for table: Parent")
        return True
    except Exception as e:
        sqlite_session.rollback()
        postgres_session.rollback()
        logging.error(f"❌ Error migrating Parent Table: {str(e)}")
        return False
    finally:
        sqlite_session.close()
        postgres_session.close()

#migrate address data
def migrate_address_data():
    """Migrate data for a specific table using SQLAlchemy."""
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    logging.info("Migrating Address data...")
    # logging.info("Migrating remote data...")
    try:
        address_data = sqlite_session.query(Address).filter(Address.is_synced==False).all()
        if len(address_data) == 0:
            logging.info(f"⚠️ No data to migrate for table: Address")
            return True  # Continue with the next table
        
        
        for row in address_data:
            # row.__delattr__("_sa_instance_state")
            row.__setattr__("is_synced", True)
            
        data_dicts = [row.__dict__ for row in address_data]
        
        postgres_session.bulk_insert_mappings(Address, data_dicts)
        postgres_session.flush()
        
        # update staff table in local db updating is_synced  == True
        sqlite_session.query(Address).filter(Address.is_synced==False).update({"is_synced":True})
        sqlite_session.commit()
        postgres_session.commit()
        logging.info(f"✅ Data migrated for table: Address")
        return True
    except Exception as e:
        sqlite_session.rollback()
        postgres_session.rollback()
        logging.error(f"❌ Error migrating Address Table: {str(e)}")
        return False
    finally:
        sqlite_session.close()
        postgres_session.close()


# migrate student data
def migrate_student_data():
    """Migrate data for a specific table using SQLAlchemy."""
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    logging.info("Migrating Student data...")
    # logging.info("Migrating remote data...")
    try:
        student_data = sqlite_session.query(Student).filter(Student.is_synced==False).all()
        if len(student_data) == 0:
            logging.info(f"⚠️ No data to migrate for table: Student")
            return True  # Continue with the next table
        data_dicts = []
        for student in student_data:
            # check for each student if corresponding Parent exists in cloud table
            parent = postgres_session.query(Parent).filter(Parent.parent_id==student.parent_id).first()
            
            # check for each student if corresponding Address exists in cloud table
            address = postgres_session.query(Address).filter(Address.address_id==student.address_id).first()
            
            # check for each student if corresponding Standard exists in cloud table
            standard = postgres_session.query(Standard).filter(Standard.standard_id==student.standard_id).first()
            
            if not parent or not address or not standard:
                # skip this student
                continue
            # update staff table in local db updating is_synced  == True
            sqlite_session.query(Student).filter(Student.student_id==student.student_id).update({"is_synced":True})
            student.__setattr__("is_synced", True)
            data_dicts.append(student.__dict__)
        
        # store the students which have their parent, address and standard id present to the cloud table
        postgres_session.bulk_insert_mappings(Student, data_dicts)
        postgres_session.flush()
        
        # commit the changes
        sqlite_session.commit()
        postgres_session.commit()
        logging.info(f"✅ Data migrated for table: Student")
        return True
    except Exception as e:
        sqlite_session.rollback()
        postgres_session.rollback()
        logging.error(f"❌ Error migrating Student Table: {str(e)}")
        return False
    finally:
        sqlite_session.close()
        postgres_session.close()    

# migrate govt_id table
def migrate_govt_id_data():
    """Migrate data for a specific table using SQLAlchemy."""
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    logging.info("Migrating GovtId data...")
    # logging.info("Migrating remote data...")
    try:
        govt_id_data = sqlite_session.query(GovtId).filter(GovtId.is_synced==False).all()
        if len(govt_id_data) == 0:
            logging.info(f"⚠️ No data to migrate for table: GovtId")
            return True  # Continue with the next table
        data_dicts = []
        for govtid in govt_id_data:
            # check if student or staff exists for govt_id
            user = None
            if(govtid.user_type == UserType.STUDENT):
                user = postgres_session.query(Student).filter(Student.student_id==govtid.user_id).first()
            elif(govtid.user_type == UserType.STAFF):
                user = postgres_session.query(Staff).filter(Staff.staff_id==govtid.user_id).first()
            if not user:
                # skip this govt_id
                continue
            # update govt_id table in local db updating is_synced  == True
            sqlite_session.query(GovtId).filter(GovtId.id==govtid.id).update({"is_synced":True})
            govtid.__setattr__("is_synced", True)
            
            match govtid.id_type:
                case "AADHAR_CARD":
                    govtid.__setattr__("id_type", GovtIdTypes.AADHAR_CARD)
                case "PAN_CARD":
                    govtid.__setattr__("id_type", GovtIdTypes.PAN_CARD)
                case "DRIVING_LICENSE":
                    govtid.__setattr__("id_type", GovtIdTypes.DRIVING_LICENSE)
                case "PASSPORT":
                    govtid.__setattr__("id_type", GovtIdTypes.PASSPORT)
                case "VOTER_ID_CARD":
                    govtid.__setattr__("id_type", GovtIdTypes.VOTER_ID_CARD)
            logging.info(f"GovtIdType : {govtid.id_type} {type(govtid.id_type)}")
            data_dicts.append(govtid.__dict__)
        
        # store the govt_ids which have their corresponding user (student or staff) in the cloud table
        postgres_session.bulk_insert_mappings(GovtId, data_dicts)
        postgres_session.flush()
        
        # commit the changes
        sqlite_session.commit()
        postgres_session.commit()
        logging.info(f"✅ Data migrated for table: GovtId")
        return True
    except Exception as e:
        sqlite_session.rollback()
        postgres_session.rollback()
        logging.error(f"❌ Error migrating GovtId Table: {str(e)}")
        return False
    finally:
        sqlite_session.close()
        postgres_session.close()

@repeat_every(seconds=60*60*24*30)
async def automatic_migration():
    logging.info("🔄 Scheduled Data migration triggered...")
    last_run = get_last_run_time()
    if last_run and last_run + timedelta(days=30) > datetime.now():
        logging.warning(f"⏳ Data Migration skipped! Last run was on {last_run}. Next allowed after {last_run + timedelta(days=30)}.")
        return  # Exit function
    await migrate_data()

async def migrate_data():
    logging.info("🔄 Migration started...")
    if check_internet():
        logging.info("🌍 Internet connected! Starting migration...")
        tables = [
            ("Staff",Staff),
            ("Standard",Standard),
            ("Parent",Parent),
            ("Address",Address),
            ("Student",Student),
            ("GovtId",GovtId)
        ]
        # for table_name, model in tables:
        failed_tables = []
        for table_name, model in tables:
            match table_name:
                case "Staff":
                    if not migrate_staff_data():
                        failed_tables.append(table_name)
                case "Standard":
                    if not migrate_standard_data():
                        failed_tables.append(table_name)
                case "Parent":
                    if not migrate_parent_data():
                        failed_tables.append(table_name)
                case "Address":
                    if not migrate_address_data():
                        failed_tables.append(table_name)
                case "Student":
                    if not migrate_student_data():
                        failed_tables.append(table_name)
                case "GovtId":
                    if not migrate_govt_id_data():
                        failed_tables.append(table_name)
        
        if failed_tables:
            logging.error(f"❌ Migration failed for tables: {', '.join(failed_tables)}")
        else:
            logging.info("✅ Migration completed successfully.")
            set_last_run_time()
    else:
        logging.error("❌ Migration failed due to no internet.")