from fastapi import FastAPI,Depends
from app.exceptions import validation_exception_handler, http_exception_handler,ResourceNotFoundException,resource_not_found_exception_handler,PasswordMismatchException,password_mismatch_exception_handler,not_permitted_exception_handler,NotPermittedException,duplicate_key_exception_handler,DuplicateKeyException,BadDataException,bad_data_exception_handler
from fastapi.exceptions import RequestValidationError,HTTPException
from app.routers import staff_router,auth_router,student_router,standard_router,attendance_router
from app.databases import Base,sqlite_engine,postgres_engine
from contextlib import asynccontextmanager
from app.crons import migrate_data,automatic_migration,migrate_attendance_data,automatic_attendance_migration
import logging
from app.routers.auth import get_current_user,check_current_user_admin
from app.models.staff import Staff,StaffRole

logging.basicConfig(filename="sync-attendance.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")



@asynccontextmanager
async def lifespan(app : FastAPI):
    await automatic_migration()
    await automatic_attendance_migration()
    logging.info("🚀 App is starting...")
    yield
    logging.info("��� App is stopping...")



app = FastAPI(lifespan=lifespan)

# router for syncing data only permitted for admin
@app.post("/sync-data")
async def sync_data(current_user : Staff = Depends(get_current_user)):
    """Sync data for all tables only permitted for admin"""
    await check_current_user_admin(current_user)
    await migrate_data()
    
@app.post("/sync-attendance")
async def sync_attendance(current_user : Staff = Depends(get_current_user)):
    """Sync data for all tables only permitted for admin"""
    await migrate_attendance_data(current_user=current_user)

        
app.include_router(staff_router,prefix="/staff",tags=["staff"])
app.include_router(auth_router,prefix="/auth",tags=["auth"])
app.include_router(student_router, prefix="/students", tags=["student"])
app.include_router(standard_router,prefix="/standard",tags=["standard"])
app.include_router(attendance_router,prefix="/attendance",tags=["standard"])

        
#exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
app.add_exception_handler(PasswordMismatchException, password_mismatch_exception_handler)
app.add_exception_handler(DuplicateKeyException, duplicate_key_exception_handler)
app.add_exception_handler(NotPermittedException, not_permitted_exception_handler)
app.add_exception_handler(BadDataException, bad_data_exception_handler)

Base.metadata.create_all(sqlite_engine)
Base.metadata.create_all(postgres_engine)

