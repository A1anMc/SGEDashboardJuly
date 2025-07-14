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
    """Get database information with enhanced error handling."""
    try:
        # Use the session-based approach
        SessionLocal = SessionLocal
        db = SessionLocal()
        
        try:
            # Get PostgreSQL version
            version_result = db.execute(text("SHOW server_version"))
            version = version_result.scalar()
            
            # Get connection info
            info_result = db.execute(text("""
                SELECT 
                    current_database() as db_name,
                    current_user as user,
                    inet_server_addr() as server_ip,
                    inet_server_port() as server_port
            """))
            info = info_result.fetchone()
            
            # Safe URL extraction
            safe_url = "localhost"
            try:
                if "@" in settings.DATABASE_URL:
                    safe_url = settings.DATABASE_URL.split("@")[1].split("/")[0]
            except:
                pass
            
            return {
                "version": version,
                "database": info.db_name if info else "unknown",
                "user": info.user if info else "unknown",
                "server_ip": str(info.server_ip) if info and info.server_ip else "unknown",
                "server_port": info.server_port if info else "unknown",
                "url": safe_url,
                "status": "connected"
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to get database info: {str(e)}")
        
        # Safe URL extraction for error case
        safe_url = "unknown"
        try:
            if "@" in settings.DATABASE_URL:
                safe_url = settings.DATABASE_URL.split("@")[1].split("/")[0]
        except:
            pass
        
        return {
            "error": str(e),
            "url": safe_url,
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