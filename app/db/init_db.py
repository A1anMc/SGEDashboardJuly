"""Database initialization module."""
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.db.session import get_db_session
from app.db.base import Base

logger = logging.getLogger(__name__)

def wait_for_db() -> bool:
    """Wait for database to be ready."""
    try:
        db = next(get_db_session())
        try:
            # Test database connection
            if settings.DATABASE_URL.startswith("postgresql"):
                result = db.execute(text("SELECT version();"))
                version = result.scalar()
                logger.info(f"Connected to PostgreSQL version: {version}")
                
                # Get current connection count
                result = db.execute(text("SELECT count(*) FROM pg_stat_activity;"))
                connections = result.scalar()
                logger.info(f"Current database connections: {connections}")
            else:
                # For SQLite, just check if we can execute a simple query
                db.execute(text("SELECT 1"))
                logger.info("Connected to SQLite database")
            
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def init_db() -> bool:
    """Initialize database with required tables."""
    try:
        # Wait for database to be ready
        if not wait_for_db():
            logger.error("Database not available after timeout")
            return False

        db = next(get_db_session())
        try:
            if settings.DATABASE_URL.startswith("postgresql"):
                # Enable PostgreSQL extensions
                extensions = [
                    "uuid-ossp",  # For UUID generation
                    "pg_trgm",    # For text search
                    "hstore",     # For key-value storage
                    "btree_gin",  # For faster indexing
                    "btree_gist"  # For range types
                ]
                
                for ext in extensions:
                    try:
                        db.execute(text(f'CREATE EXTENSION IF NOT EXISTS "{ext}";'))
                        logger.info(f"Extension {ext} initialized successfully")
                    except SQLAlchemyError as e:
                        logger.warning(f"Failed to create extension {ext}: {str(e)}")
                
                logger.info("Database extensions initialized successfully")
            elif settings.DATABASE_URL.startswith("sqlite"):
                # Enable SQLite foreign key support
                db.execute(text("PRAGMA foreign_keys=ON"))
                logger.info("SQLite foreign key support enabled")
            
            # Create all tables
            Base.metadata.create_all(bind=db.get_bind())
            logger.info("Database tables created successfully")
            
            return True
        finally:
            db.close()
            
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

def check_db_health() -> bool:
    """Check database health."""
    try:
        db = next(get_db_session())
        try:
            # Test database connection
            if settings.DATABASE_URL.startswith("postgresql"):
                result = db.execute(text("SELECT 1"))
            else:
                result = db.execute(text("SELECT 1"))
            
            if result.scalar() == 1:
                logger.info("Database health check passed")
                return True
            else:
                logger.error("Database health check failed: unexpected result")
                return False
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False 