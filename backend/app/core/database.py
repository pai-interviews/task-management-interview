from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from .config import settings

# Configure database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Configure engine with proper settings
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=False  # Set to True for SQL query logging in development
    )
else:
    # PostgreSQL/MySQL configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Database dependency that provides a database session.
    Ensures proper cleanup and error handling.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logging.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
