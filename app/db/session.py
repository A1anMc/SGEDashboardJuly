from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.pool import QueuePool
import time
import logging
from contextlib import contextmanager

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def create_db_engine():
    """Create database engine with retry logic and proper configuration."""
    connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
    
    for attempt in range(settings.DATABASE_RETRY_LIMIT):
        try:
            engine = create_engine(
                settings.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_timeout=settings.DATABASE_POOL_TIMEOUT,
                pool_recycle=settings.DATABASE_POOL_RECYCLE,
                echo=settings.DATABASE_ECHO,
                connect_args=connect_args
            )
            
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return engine
            
        except OperationalError as e:
            if attempt < settings.DATABASE_RETRY_LIMIT - 1:
                logger.warning(f"Database connection attempt {attempt + 1} failed. Retrying in {settings.DATABASE_RETRY_DELAY} seconds...")
                time.sleep(settings.DATABASE_RETRY_DELAY)
            else:
                logger.error("Failed to connect to database after multiple attempts")
                raise e
        except Exception as e:
            logger.error(f"Unexpected error while connecting to database: {str(e)}")
            raise e

# Create engine with retry logic
engine = create_db_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    """Database session context manager with error handling."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during database operation: {str(e)}")
        raise
    finally:
        db.close()

# Dependency to get database session
def get_db_session():
    """FastAPI dependency for database sessions."""
    with get_db() as session:
        yield session 