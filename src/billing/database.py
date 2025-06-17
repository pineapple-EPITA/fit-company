from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get database URL from environment variable or use default
DATABASE_URL = os.getenv("BILLING_DATABASE_URL", "sqlite:///./billing.db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def init_db():
    """Initialize the database by creating all tables"""
    Base.metadata.create_all(bind=engine)

def db_session():
    """Get a database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 