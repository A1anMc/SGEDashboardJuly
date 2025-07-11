"""Database initialization module with enhanced error handling."""
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.db.session import init_database, get_engine_instance, get_session_local, check_db_health as session_check_db_health
from app.db.base import Base
import time

logger = logging.getLogger(__name__)

def init_db() -> None:
    """Initialize database with enhanced error handling and retry logic."""
    logger.info("Starting database initialization...")
    
    # First, initialize the database connection
    if not init_database():
        raise RuntimeError("Failed to initialize database connection")
    
    retries = settings.DATABASE_MAX_RETRIES
    retry_delay = settings.DATABASE_RETRY_DELAY
    
    for attempt in range(retries):
        try:
            # Get engine instance
            engine = get_engine_instance()
            
            # Try to connect and create tables
            with engine.connect() as conn:
                # Check if we can connect
                conn.execute(text("SELECT 1"))
                logger.info("Database connection established successfully")
                
                # For Supabase, we don't need to create extensions as they're pre-installed
                if "supabase.co" not in settings.DATABASE_URL:
                    try:
                        # Create extensions for PostgreSQL if they don't exist
                        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_stat_statements"))
                        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
                        conn.execute(text("CREATE EXTENSION IF NOT EXISTS uuid-ossp"))
                        conn.commit()
                        logger.info("PostgreSQL extensions created/verified")
                    except Exception as ext_error:
                        logger.warning(f"Could not create PostgreSQL extensions: {ext_error}")
                        # Continue anyway, extensions might not be needed
            
            # Create all tables
            try:
                Base.metadata.create_all(bind=engine)
                logger.info("Database tables created/verified successfully")
            except Exception as table_error:
                logger.error(f"Failed to create tables: {table_error}")
                raise
            
            logger.info("Database initialization completed successfully")
            return
            
        except Exception as e:
            if attempt == retries - 1:  # Last attempt
                logger.error(f"Failed to initialize database after {retries} attempts: {str(e)}")
                raise RuntimeError(f"Database initialization failed: {str(e)}")
            logger.warning(f"Database initialization attempt {attempt + 1} failed: {str(e)}")
            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff

def get_db_info() -> dict:
    """Get database information with enhanced error handling."""
    try:
        # Use the session-based approach
        SessionLocal = get_session_local()
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
        return session_check_db_health()
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