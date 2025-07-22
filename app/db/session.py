import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import time

# Configure logging
logger = logging.getLogger(__name__)

# Global engine variable
_engine = None
_SessionLocal = None

# Global error tracking
_last_connection_error = None

def get_engine():
    """Create SQLAlchemy engine with absolute minimal configuration."""
    global _engine
    
    if _engine is not None:
        return _engine
    
    # Get DATABASE_URL
    database_url = settings.DATABASE_URL
    
    if not database_url:
        if settings.ENV == "production":
            raise RuntimeError("DATABASE_URL environment variable is required in production")
        else:
            database_url = "postgresql://alanmccarthy@localhost:5432/navimpact_db"
    
    try:
        # Create engine with minimal configuration
        _engine = create_engine(database_url)
        
        # Test connection
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        logger.info("Database connection successful")
        return _engine
        
    except Exception as e:
        error_msg = f"Failed to create database engine: {str(e)}"
        logger.error(error_msg)
        global _last_connection_error
        _last_connection_error = {"error": error_msg, "timestamp": time.time()}
        raise RuntimeError(error_msg)

def get_session_local():
    """Get database session factory."""
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal

def close_database():
    """Close database connections."""
    global _engine
    if _engine:
        _engine.dispose()
        logger.info("Database connections closed")

def get_last_connection_error():
    """Get the last database connection error."""
    global _last_connection_error
    return _last_connection_error

def get_db():
    """Get database session with automatic closing."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def health_check():
    """Check database health."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False 