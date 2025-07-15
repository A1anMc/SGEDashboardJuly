import os
import socket
from urllib.parse import urlparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global engine variable (will be initialized lazily)
_engine: Optional[object] = None
_SessionLocal: Optional[sessionmaker] = None
_last_connection_error: Optional[Dict[str, Any]] = None

def resolve_database_host(url: str) -> str:
    """Resolve database hostname and return updated URL."""
    parsed = urlparse(url)
    if not parsed.hostname:
        return url
    
    try:
        # Try to resolve the hostname directly
        logger.info(f"Attempting to resolve hostname: {parsed.hostname}")
        socket.gethostbyname(parsed.hostname)
        return url
    except socket.gaierror as e:
        logger.error(f"Failed to resolve hostname {parsed.hostname}: {e}")
        
        # Check if hostname is from Render's database
        if "render.com" in parsed.hostname:
            alt_domains = [
                parsed.hostname.replace("dpg-", "oregon-postgres-"),
                parsed.hostname.replace("dpg-", "frankfurt-postgres-"),
                f"{parsed.hostname}.render-databases.com",
                f"{parsed.hostname}.internal-database.render.com",
                f"{parsed.hostname}.postgres.render.com",
                # Add more specific Render domains
                f"{parsed.hostname}.oregon.render.com",
                f"{parsed.hostname}.frankfurt.render.com",
                f"{parsed.hostname}.singapore.render.com"
            ]
            
            for alt_domain in alt_domains:
                try:
                    logger.info(f"Trying alternative domain: {alt_domain}")
                    socket.gethostbyname(alt_domain)
                    new_url = url.replace(parsed.hostname, alt_domain)
                    logger.info(f"Using alternative database URL with domain: {alt_domain}")
                    return new_url
                except socket.gaierror:
                    continue
        
        # If all attempts fail, return original URL
        return url

def get_engine(url=None, **kwargs):
    """Create SQLAlchemy engine with retry logic and proper configuration."""
    global _last_connection_error
    final_url = url or settings.DATABASE_URL
    
    # Validate database URL - no localhost fallbacks in production
    if not final_url:
        if settings.ENV == "production":
            error_msg = "DATABASE_URL environment variable is required in production"
            logger.error(error_msg)
            _last_connection_error = {"error": error_msg, "timestamp": time.time()}
            raise RuntimeError(error_msg)
        else:
            final_url = "postgresql://alanmccarthy@localhost:5432/sge_dashboard"
            logger.info("No DATABASE_URL provided, using local PostgreSQL for development")
    
    # Check for localhost in production
    if settings.ENV == "production" and ("localhost" in final_url or "127.0.0.1" in final_url):
        error_msg = "DATABASE_URL cannot use localhost in production environment"
        logger.error(error_msg)
        _last_connection_error = {"error": error_msg, "timestamp": time.time()}
        raise RuntimeError(error_msg)
    
    # Validate database URL format
    if not final_url.startswith("postgresql://"):
        error_msg = f"DATABASE_URL must start with postgresql:// (got: {final_url.split('://')[0] if '://' in final_url else 'invalid'})"
        logger.error(error_msg)
        _last_connection_error = {"error": error_msg, "timestamp": time.time()}
        raise RuntimeError(error_msg)
    
    # Try to resolve hostname and get working URL
    final_url = resolve_database_host(final_url)
    
    logger.info(f"Connecting to database: {final_url.split('@')[0] if '@' in final_url else final_url.split('://')[0]}://***")
    
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
    
    # Add PostgreSQL-specific settings
    engine_args.update({
        "connect_args": {
            "application_name": "sge-dashboard-api",
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5,
            "connect_timeout": int(os.getenv("PGCONNECT_TIMEOUT", "10")),
            "options": "-c timezone=UTC -c datestyle=ISO,MDY",
            "client_encoding": "utf8"
        }
    })
    
    # SSL settings are handled by the DATABASE_URL itself
    # No need to add additional SSL configuration here
    
    # Update with any additional arguments
    engine_args.update(kwargs)
    
    # Create engine with retry logic
    retries = settings.DATABASE_MAX_RETRIES
    retry_delay = settings.DATABASE_RETRY_DELAY
    
    last_error = None
    for attempt in range(retries):
        try:
            engine = create_engine(final_url, **engine_args)
            # Test the connection only if not in testing mode
            if not settings.TESTING:
                with engine.connect() as conn:
                    # More comprehensive connection test
                    result = conn.execute(text("""
                        SELECT current_database() as db,
                               current_user as user,
                               version() as version,
                               inet_server_addr() as server_addr
                    """)).fetchone()
                    logger.info(f"Database connection test successful: {dict(result)}")
                    _last_connection_error = None  # Clear any previous error
            return engine
        except Exception as e:
            last_error = str(e)
            if attempt == retries - 1:  # Last attempt
                error_msg = f"Failed to connect to database after {retries} attempts: {last_error}"
                logger.error(error_msg)
                _last_connection_error = {
                    "error": error_msg,
                    "last_attempt": time.time(),
                    "attempts": retries,
                    "last_error": last_error
                }
                raise RuntimeError(error_msg)
            logger.warning(f"Database connection attempt {attempt + 1} failed: {last_error}")
            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff

def get_last_connection_error() -> Optional[Dict[str, Any]]:
    """Get information about the last connection error."""
    return _last_connection_error

def get_engine_instance():
    """Get the global engine instance, creating it if necessary."""
    global _engine
    if _engine is None:
        _engine = get_engine()
        # Initialize pool monitor when engine is created
        try:
            from app.db.pool_monitor import initialize_pool_monitor
            initialize_pool_monitor(_engine)
        except Exception as e:
            logger.warning(f"Failed to initialize pool monitor: {e}")
    return _engine

def get_session_local():
    """Get the SessionLocal factory, creating it if necessary."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine_instance()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal

# Lazy initialization - these will be created when first accessed
@property
def engine():
    """Lazy engine property."""
    return get_engine_instance()

@property
def SessionLocal():
    """Lazy SessionLocal property."""
    return get_session_local()

@contextmanager
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
    """Check database health with proper error handling."""
    try:
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            result = db.execute(text("SELECT 1"))
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

def init_database():
    """Initialize database connection and test it."""
    try:
        engine = get_engine_instance()
        logger.info("Database engine initialized successfully")
        
        # Test connection
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

# For backward compatibility, create lazy properties
class LazyEngine:
    def __getattr__(self, name):
        return getattr(get_engine_instance(), name)
    
    def connect(self):
        return get_engine_instance().connect()
    
    def execute(self, *args, **kwargs):
        return get_engine_instance().execute(*args, **kwargs)
    
    def dispose(self):
        return get_engine_instance().dispose()

class LazySessionLocal:
    def __call__(self, *args, **kwargs):
        return get_session_local()(*args, **kwargs)

# Create lazy instances for backward compatibility
engine = LazyEngine()
SessionLocal = LazySessionLocal() 