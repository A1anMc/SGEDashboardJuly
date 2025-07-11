import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging
import time
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_engine(url=None, **kwargs):
    """Create SQLAlchemy engine with retry logic and proper configuration."""
    final_url = url or settings.DATABASE_URL
    
    # Default engine arguments
    engine_args = {
        "pool_pre_ping": True,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
        "pool_recycle": settings.DATABASE_POOL_RECYCLE,
        "echo": settings.DATABASE_ECHO,
        "poolclass": QueuePool,
    }
    
    # Add Supabase-specific settings if using Supabase
    if "supabase.co" in final_url:
        engine_args.update({
            "connect_args": {
                "application_name": "sge-dashboard-api",
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
                "sslmode": "require"
            }
        })
    
    # Update with any additional arguments
    engine_args.update(kwargs)
    
    # Create engine with retry logic
    retries = settings.DATABASE_MAX_RETRIES
    retry_delay = settings.DATABASE_RETRY_DELAY
    
    for attempt in range(retries):
        try:
            engine = create_engine(final_url, **engine_args)
            # Test the connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return engine
        except Exception as e:
            if attempt == retries - 1:  # Last attempt
                logger.error(f"Failed to connect to database after {retries} attempts: {str(e)}")
                raise
            logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff

# Create engine
engine = get_engine()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db():
    """Get database session with automatic closing."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Get a database session (to be used as a FastAPI dependency)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_health() -> bool:
    """Check database health."""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False
    finally:
        db.close() 