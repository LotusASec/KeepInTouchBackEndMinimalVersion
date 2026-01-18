"""Database configuration and session management"""
import os
import sqlite3
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import SQLALCHEMY_DATABASE_URL

# For SQLite, ensure the database file and directory can be created
if SQLALCHEMY_DATABASE_URL.startswith("sqlite://"):
    # Parse the database path
    db_url = SQLALCHEMY_DATABASE_URL
    if db_url.startswith("sqlite:///"):
        db_path = db_url[10:]  # Remove "sqlite:///" prefix
    else:
        db_path = db_url[7:]   # Remove "sqlite://" prefix
    
    # Create directory if needed
    if db_path and db_path != ":memory:":
        db_dir = os.path.dirname(os.path.abspath(db_path))
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except Exception:
                pass
        
        # Ensure file can be created/accessed
        abs_path = os.path.abspath(db_path)
        # Replace the URL with absolute path
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{abs_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Enable foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    if isinstance(dbapi_conn, sqlite3.Connection):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
