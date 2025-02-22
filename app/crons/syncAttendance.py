from fastapi_utils.tasks import repeat_every
import logging
from app.models import Student,Staff,Standard,Attendance
from datetime import datetime, timedelta
from .utils import PostgresSession,get_last_run_time,set_last_run_time,SQLiteSession,check_internet


# Configure logging
logging.basicConfig(filename="sync-data.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@repeat_every(seconds=60*60*12)
async def automatic_attendance_migration():
    
    logging.info("🔄 Scheduled Attendance migration triggered...")
    last_run = get_last_run_time(for_attendance=True)
    if last_run and last_run + timedelta(hours=12) > datetime.now():
        logging.warning(f"⏳ Attendance Migration skipped! Last run was on {last_run}. Next allowed after {last_run + timedelta(days=30)}.")
        return  # Exit function
    await migrate_attendance_data()
    
async def migrate_attendance_data(current_user : Staff | None = None):
    """Sync attendance data to the cloud database"""
    logging.info("🔄 Attendance Migration started...")
    if check_internet():
        logging.info("🌍 Internet connected! Starting Attendance migration...")
        sqlite_session = SQLiteSession()
        postgres_session = PostgresSession()
        logging.info("Migrating Attendance data...")
        is_synced = False
        try:
            # check which type of staff is current_user and if teacher only migrate its standard data 
            attendance_data= []
            if current_user:
                # find the standard of the current user
                standard = sqlite_session.query(Standard).filter(Standard.class_teacher_id==current_user.staff_id).first()
                if standard:
                    attendance_data = sqlite_session.query(Attendance).filter(Attendance.standard_id==standard.standard_id).filter(Attendance.is_synced==False).all()
            else:
                # get all attendance records
                attendance_data = sqlite_session.query(Attendance).filter(Attendance.is_synced==False).all()
            if len(attendance_data) == 0:
                logging.info(f"⚠️ No data to migrate for table: Attendance")
                # Continue with the next table
                is_synced = True
            else:
                data_dicts = []
                for attendance in attendance_data:
                    # check for each attendance if corresponding Student exists in cloud table
                    student = postgres_session.query(Student).filter(Student.student_id==attendance.student_id).first()
                    
                    # check for each attendance if corresponding Standard exists in cloud table
                    standard = postgres_session.query(Standard).filter(Standard.standard_id==attendance.standard_id).first()

                    # check for each attendance if corresponding Staff exists in cloud table
                    staff = postgres_session.query(Staff).filter(Staff.staff_id==attendance.recorded_by_id).first()

                    if not student or not standard or not staff:
                        # skip this attendance
                        continue 
                    # update Attendance table in local db deleting synced data
                    sqlite_session.query(Attendance).filter(Attendance.attendance_id==attendance.attendance_id).delete()
                    attendance.__setattr__("is_synced", True)
                    data_dicts.append(attendance.__dict__)
                
                # store the attendance which have their student, standard and staff id present to the cloud table
                postgres_session.bulk_insert_mappings(Attendance, data_dicts)
                postgres_session.flush()
                
                
                # commit the changes
                postgres_session.commit()
                sqlite_session.commit()
                is_synced = True
                set_last_run_time(for_attendance=True)
                logging.info(f"�� Data migrated for table: Attendance")
        except Exception as e:
            logging.error(f"🚫 Error migrating Attendance data: {e}")
            sqlite_session.rollback()
            postgres_session.rollback()
            is_synced = False
        finally:
            sqlite_session.close()
            postgres_session.close()
        if is_synced:
            logging.info("✅ Attendance Migration completed!")
        else:
            logging.error("⚠️ Attendance Migration failed!")
    else:
        logging.error("🚫 Internet not connected! Attendance Migration failed!")
                