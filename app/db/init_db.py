"""Database initialization module."""
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.db.session import engine, get_db
from app.db.base import Base
import time

logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize database with retry logic."""
    retries = settings.DATABASE_MAX_RETRIES
    retry_delay = settings.DATABASE_RETRY_DELAY
    
    for attempt in range(retries):
        try:
            # Try to connect and create tables
            with engine.connect() as conn:
                # Check if we can connect
                conn.execute(text("SELECT 1"))
                
                # For Supabase, we don't need to create extensions as they're pre-installed
                if "supabase.co" not in settings.DATABASE_URL:
                    # Create extensions for PostgreSQL if they don't exist
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_stat_statements"))
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS uuid-ossp"))
                    conn.commit()
            
            # Create all tables
            Base.metadata.create_all(bind=engine)
            logger.info("Database initialized successfully")
            return
            
        except Exception as e:
            if attempt == retries - 1:  # Last attempt
                logger.error(f"Failed to initialize database after {retries} attempts: {str(e)}")
                raise
            logger.warning(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff

def get_db_info() -> dict:
    """Get database information."""
    try:
        with get_db() as db:
            # Get PostgreSQL version
            version = db.execute(text("SHOW server_version")).scalar()
            
            # Get connection info
            info = db.execute(text("""
                SELECT 
                    current_database() as db_name,
                    current_user as user,
                    inet_server_addr() as server_ip,
                    inet_server_port() as server_port
            """)).fetchone()
            
            return {
                "version": version,
                "database": info.db_name,
                "user": info.user,
                "server_ip": str(info.server_ip),
                "server_port": info.server_port,
                "url": settings.DATABASE_URL.split("@")[1].split("/")[0]  # Safe part of the URL
            }
    except Exception as e:
        logger.error(f"Failed to get database info: {str(e)}")
        return {
            "error": str(e),
            "url": settings.DATABASE_URL.split("@")[1].split("/")[0]  # Safe part of the URL
        }

def check_db_health() -> bool:
    """Check database health."""
    try:
        with get_db() as db:
            # Test database connection
            result = db.execute(text("SELECT 1"))
            if result.scalar() == 1:
                logger.info("Database health check passed")
                return True
            else:
                logger.error("Database health check failed: unexpected result")
                return False
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False 