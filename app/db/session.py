import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Configure engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,  # Set connection pool size
    max_overflow=10  # Allow up to 10 connections beyond pool_size
)

# Create session factory
SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)

def get_db_session():
    """Get database session."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()  # Close session
        SessionLocal.remove()  # Remove session from registry

def check_db_health() -> bool:
    """Check database health."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False
    finally:
        db.close() 