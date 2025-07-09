from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.pool import QueuePool
import time
import logging
from contextlib import contextmanager
from typing import Generator
import backoff  # We'll need to add this to requirements.txt
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(".envV2")

from app.core.config import settings

def is_retriable_error(e):
    """Determine if an error should trigger a retry."""
    if isinstance(e, OperationalError):
        # Check for specific error messages that indicate retry-able errors
        error_msg = str(e).lower()
        retry_messages = [
            "connection refused",
            "too many connections",
            "connection timed out",
            "deadlock detected",
            "lost connection",
        ]
        return any(msg in error_msg for msg in retry_messages)
    return False

@backoff.on_exception(
    backoff.expo,
    OperationalError,
    max_tries=settings.DATABASE_MAX_RETRIES,
    giveup=lambda e: not is_retriable_error(e),
    on_backoff=lambda details: logger.warning(
        f"Database connection attempt {details['tries']} failed. "
        f"Retrying in {details['wait']:.1f} seconds..."
    )
)
def create_db_engine():
    """Create database engine with retry logic and proper configuration."""
    try:
        # Use hardcoded database URL for local development
        database_url = "postgresql://alanmccarthy@localhost:5432/sge_dashboard"
        logger.info(f"Creating engine with URL: {database_url}")
        
        engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_timeout=settings.DATABASE_POOL_TIMEOUT,
            pool_pre_ping=True,
            pool_recycle=settings.DATABASE_POOL_RECYCLE,
            echo=settings.DATABASE_ECHO,
            connect_args={
                "connect_timeout": settings.DATABASE_CONNECT_TIMEOUT,
                "keepalives": 1 if settings.DATABASE_KEEPALIVES else 0,
                "keepalives_idle": settings.DATABASE_KEEPALIVES_IDLE,
                "keepalives_interval": settings.DATABASE_KEEPALIVES_INTERVAL,
                "keepalives_count": settings.DATABASE_KEEPALIVES_COUNT
            }
        )
        
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection established successfully")
        
        return engine
            
    except Exception as e:
        logger.error(f"Failed to create database engine: {str(e)}")
        raise

# Create engine with retry logic
engine = create_db_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db() -> Generator:
    """Database session context manager with error handling and connection verification."""
    db = SessionLocal()
    try:
        # Verify connection is alive
        db.execute(text("SELECT 1"))
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

def check_db_health() -> bool:
    """Check database health and connection pool status."""
    try:
        with get_db() as db:
            # Basic connection test
            db.execute(text("SELECT 1"))
            
            # Get pool statistics
            pool = engine.pool
            logger.info(
                f"Database pool status - "
                f"Size: {pool.size()}, "
                f"Checked out: {pool.checkedout()}, "
                f"Overflow: {pool.overflow()}"
            )
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

# Dependency to get database session
def get_db_session() -> Generator:
    """FastAPI dependency for database sessions."""
    with get_db() as session:
        yield session 