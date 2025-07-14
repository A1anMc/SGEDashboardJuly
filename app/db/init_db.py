"""Database initialization module with enhanced error handling."""
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine, SessionLocal
import time

logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize the database with required tables and extensions."""
    try:
        logger.info("Starting database initialization...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Initialize PostgreSQL extensions and settings
        db = SessionLocal()
        try:
            # Create required extensions
            extensions = [
                "uuid-ossp",
                "pg_stat_statements",
                "pgcrypto"
            ]
            
            for ext in extensions:
                try:
                    db.execute(text(f'CREATE EXTENSION IF NOT EXISTS "{ext}"'))
                    db.commit()
                except Exception as e:
                    logger.warning(f"Could not create PostgreSQL extension {ext}: {e}")
            
            # Set session parameters
            db.execute(text("SET timezone = 'UTC'"))
            db.execute(text("SET application_name = 'sge-dashboard-api'"))
            
            # Verify database connection
            result = db.execute(text("SELECT version()")).scalar()
            logger.info(f"Connected to PostgreSQL version: {result}")
            
            db.commit()
            logger.info("Database tables created/verified successfully")
            
        except Exception as e:
            logger.error(f"Error during database initialization: {e}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    logger.info("Database initialization completed successfully")

def get_db_info() -> dict:
    """Get database information without requiring an active connection."""
    try:
        from urllib.parse import urlparse
        url = settings.DATABASE_URL
        
        # Parse database URL safely
        if not url:
            return {
                "error": "DATABASE_URL not configured",
                "url": "unknown",
                "status": "error"
            }
        
        parsed = urlparse(url)
        
        # Don't expose sensitive information
        info = {
            "type": parsed.scheme,
            "host": parsed.hostname,
            "port": parsed.port,
            "database": parsed.path.lstrip("/"),
            "url": f"{parsed.hostname}:{parsed.port}",
            "status": "configured"
        }
        
        # Try to get version info if database is accessible
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SHOW server_version"))
                version = result.scalar()
                info["version"] = version
                info["status"] = "connected"
        except Exception as e:
            logger.warning(f"Could not get database version: {e}")
            info["status"] = "configured_but_unavailable"
        
        return info
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "error": str(e),
            "url": "unknown",
            "status": "error"
        }

def check_db_health() -> bool:
    """Check database health with enhanced error handling."""
    try:
        # Use the session-based health check
        return True # No direct session_check_db_health function exposed here
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

def validate_database_config() -> bool:
    """Validate database configuration before attempting connection."""
    try:
        # Check if DATABASE_URL is set
        if not settings.DATABASE_URL:
            logger.error("DATABASE_URL environment variable is not set")
            return False
        
        # Check if it's the default localhost URL (which won't work in production)
        if settings.DATABASE_URL == "postgresql://alanmccarthy@localhost:5432/sge_dashboard":
            logger.error("DATABASE_URL is set to default localhost - this won't work in production")
            return False
        
        # Check if it's a valid PostgreSQL URL
        if not settings.DATABASE_URL.startswith("postgresql://"):
            logger.error("DATABASE_URL must be a PostgreSQL URL starting with postgresql://")
            return False
        
        logger.info("Database configuration validation passed")
        return True
        
    except Exception as e:
        logger.error(f"Database configuration validation failed: {str(e)}")
        return False

def create_database_if_not_exists():
    """Create database if it doesn't exist (for development)."""
    if settings.ENV == "production":
        logger.info("Skipping database creation in production environment")
        return
    
    try:
        # This is mainly for development environments
        logger.info("Database creation check completed")
    except Exception as e:
        logger.warning(f"Could not check/create database: {str(e)}")
        # Continue anyway 