from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
import time

<<<<<<< HEAD
# Get database URL from environment variable or use default
=======
# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Get database URL from environment variable
>>>>>>> a1837601b151a674de05520f8ccaf6ebedb62b3d
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:docker@billing-db:5432/billing-db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

def init_db():
    """Initialize the database by creating all tables with retry logic"""
    max_retries = 5
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to initialize database (attempt {attempt + 1}/{max_retries})")
            Base.metadata.create_all(bind=engine)
            logger.info("Database initialized successfully")
            return
        except Exception as e:
            logger.error(f"Failed to initialize database (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached. Giving up on database initialization.")
                raise

def db_session():
    """Get a database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close() 