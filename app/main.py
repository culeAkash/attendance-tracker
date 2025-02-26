from fastapi import FastAPI,Depends
from app.exceptions import validation_exception_handler, http_exception_handler,ResourceNotFoundException,resource_not_found_exception_handler,PasswordMismatchException,password_mismatch_exception_handler,not_permitted_exception_handler,NotPermittedException,duplicate_key_exception_handler,DuplicateKeyException,BadDataException,bad_data_exception_handler
from fastapi.exceptions import RequestValidationError,HTTPException
from app.routers import staff_router,auth_router,student_router,standard_router,attendance_router,upload_file_router
from app.databases import Base,sqlite_engine,postgres_engine
from contextlib import asynccontextmanager
from app.crons import migrate_data,automatic_migration,migrate_attendance_data,automatic_attendance_migration
import logging
from app.utils.auth import get_current_user,check_current_user_admin
from app.models import Staff
import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(filename="sync-attendance.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define Upload Directories
UPLOAD_DIR = "uploads"
STUDENT_DIR = os.path.join(UPLOAD_DIR, "students")
STAFF_DIR = os.path.join(UPLOAD_DIR, "staff")

# Ensure directories exist
os.makedirs(STUDENT_DIR, exist_ok=True)
os.makedirs(STAFF_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app : FastAPI):
    await automatic_migration()
    await automatic_attendance_migration()
    logging.info("🚀 App is starting...")
    yield
    logging.info("��� App is stopping...")



app = FastAPI(lifespan=lifespan)


# Define allowed origins
origins = [
    "http://localhost",
    "http://localhost:5173",  # Allow frontend running on port 3000
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Mount static directories for serving images
app.mount("/uploads/students", StaticFiles(directory=STUDENT_DIR), name="students")
app.mount("/uploads/staff", StaticFiles(directory=STAFF_DIR), name="staff")

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
app.include_router(attendance_router,prefix="/attendance",tags=["attendance"])
app.include_router(upload_file_router,prefix="/upload",tags=["upload"])

        
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

