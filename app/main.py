from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.databases import Base,SqliteSessionLocal,PostgresSessionLocal,sqlite_engine,postgres_engine
from app.routers.staff import staff_router

app = FastAPI()
# Dependency to get database session

        
app.include_router(staff_router,prefix="/staff",tags=["staff"])
        
