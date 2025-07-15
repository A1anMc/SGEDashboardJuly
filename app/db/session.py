import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Global engine variable
_engine = None
_SessionLocal = None

def get_engine():
    """Create SQLAlchemy engine with minimal configuration."""
    global _engine
    
    if _engine is not None:
        return _engine
    
    # Get DATABASE_URL
    database_url = settings.DATABASE_URL
    
    if not database_url:
        if settings.ENV == "production":
            raise RuntimeError("DATABASE_URL environment variable is required in production")
        else:
            database_url = "postgresql://alanmccarthy@localhost:5432/sge_dashboard"
    
    logger.info(f"Connecting to database: {database_url.split('@')[0] if '@' in database_url else database_url.split('://')[0]}://***")
    
    # Create engine with minimal configuration
    _engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=900,
        echo=False
    )
    
    return _engine

def get_session_local():
    """Get the SessionLocal factory."""
    global _SessionLocal
    
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    return _SessionLocal

def get_db():
    """Get database session with automatic closing."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Get a database session (to be used as a FastAPI dependency)."""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session_sync():
    """Get a database session for synchronous use (non-FastAPI)."""
    SessionLocal = get_session_local()
    return SessionLocal()

def check_db_health() -> bool:
    """Check database health with simple test."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

def init_database():
    """Initialize database connection and test it."""
    try:
        engine = get_engine()
        logger.info("Database engine initialized successfully")
        
        if check_db_health():
            logger.info("Database health check passed")
            return True
        else:
            logger.error("Database health check failed")
            return False
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        return False

def close_database():
    """Close database connections."""
    global _engine, _SessionLocal
    try:
        if _engine:
            _engine.dispose()
            _engine = None
        if _SessionLocal:
            _SessionLocal = None
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")

# For backward compatibility
engine = get_engine
SessionLocal = get_session_local 