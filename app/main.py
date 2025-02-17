from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .databases import SqliteSessionLocal,PostgresSessionLocal


app = FastAPI()

# Dependency to get database session
def get_sqlite_db():
    db = SqliteSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_postgres_db():
    db = PostgresSessionLocal()
    try:
        yield db
    finally:
        db.close()