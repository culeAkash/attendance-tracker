from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.databases import Base,SqliteSessionLocal,PostgresSessionLocal,sqlite_engine,postgres_engine
from app.routers.staff import staff_router
from app.exceptions import validation_exception_handler, http_exception_handler,ResourceNotFoundException,resource_not_found_exception_handler,PasswordMismatchException,password_mismatch_exception_handler,duplicate_key_exception_handler,DuplicateKeyException
from fastapi.exceptions import RequestValidationError,HTTPException
from app.routers.auth import auth_router


app = FastAPI()
# Dependency to get database session

        
app.include_router(staff_router,prefix="/staff",tags=["staff"])
app.include_router(auth_router,prefix="/auth",tags=["auth"])
        
#exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
app.add_exception_handler(PasswordMismatchException, password_mismatch_exception_handler)
app.add_exception_handler(DuplicateKeyException, duplicate_key_exception_handler)