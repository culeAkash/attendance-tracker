from fastapi import FastAPI
from app.exceptions import validation_exception_handler, http_exception_handler,ResourceNotFoundException,resource_not_found_exception_handler,PasswordMismatchException,password_mismatch_exception_handler,not_permitted_exception_handler,NotPermittedException,duplicate_key_exception_handler,DuplicateKeyException,BadDataException,bad_data_exception_handler
from fastapi.exceptions import RequestValidationError,HTTPException
from app.routers import staff_router,auth_router,student_router,standard_router,attendance_router
from app.databases import Base,sqlite_engine,postgres_engine


app = FastAPI()
# Dependency to get database session

        
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