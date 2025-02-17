import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import Base
from dotenv import load_dotenv

load_dotenv()
SQLITE_DATABASE_URL = os.environ.get('SQLITE_DATABASE_URL')
POSTGRES_DATABASE_URL = os.getenv('POSTGRES_DATABASE_URL')

# SQLITE Database configuration

print(SQLITE_DATABASE_URL,POSTGRES_DATABASE_URL)
# For SQLite, ensure thread safety
connect_args = {"check_same_thread": False} if "sqlite" in SQLITE_DATABASE_URL else {}
# Create engine
sqlite_engine = create_engine(SQLITE_DATABASE_URL, connect_args=connect_args)
# Session factory
SqliteSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)
# Base class for models
Base.metadata.create_all(sqlite_engine)


# SQLITE Database configuration

# Create engine
postgres_engine = create_engine(POSTGRES_DATABASE_URL)
# Session factory
PostgresSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)
# Base class for models
Base.metadata.create_all(postgres_engine)