import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.core.config import settings
import logging
import time
from contextlib import contextmanager
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global engine variable (will be initialized lazily)
_engine: Optional[object] = None
_SessionLocal: Optional[sessionmaker] = None

def get_engine(url=None, **kwargs):
    """Create SQLAlchemy engine with retry logic and proper configuration."""
    final_url = url or settings.DATABASE_URL
    
    # Validate database URL - no localhost fallbacks in production
    if not final_url:
        if settings.ENV == "production":
            error_msg = "DATABASE_URL environment variable is required in production"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        else:
            # Use SQLite for development if no DATABASE_URL is provided
            final_url = "sqlite:///./dev.db"
            logger.info("No DATABASE_URL provided, using SQLite for development")
    
    # Check for localhost in production
    if settings.ENV == "production" and ("localhost" in final_url or "127.0.0.1" in final_url):
        error_msg = "DATABASE_URL cannot use localhost in production environment"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    # Validate database URL format
    if not final_url.startswith(("postgresql://", "sqlite:///")):
        error_msg = f"DATABASE_URL must start with postgresql:// or sqlite:/// (got: {final_url[:20]}...)"
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
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
    if final_url.startswith("postgresql://"):
        engine_args.update({
            "connect_args": {
                "application_name": "sge-dashboard-api",
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            }
        })
        
        # Add SSL settings for production databases
        if settings.ENV == "production" or "supabase.co" in final_url or "render.com" in final_url:
            engine_args["connect_args"]["sslmode"] = "require"
    
    # Update with any additional arguments
    engine_args.update(kwargs)
    
    # Create engine with retry logic
    retries = settings.DATABASE_MAX_RETRIES
    retry_delay = settings.DATABASE_RETRY_DELAY
    
    for attempt in range(retries):
        try:
            engine = create_engine(final_url, **engine_args)
            # Test the connection only if not in testing mode
            if not settings.TESTING:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    logger.info("Database connection test successful")
            return engine
        except Exception as e:
            if attempt == retries - 1:  # Last attempt
                logger.error(f"Failed to connect to database after {retries} attempts: {str(e)}")
                # Provide helpful error message for common issues
                if "Connection refused" in str(e):
                    logger.error("Database connection refused. Please check:")
                    logger.error("1. DATABASE_URL environment variable is set correctly")
                    logger.error("2. Database server is running and accessible")
                    logger.error("3. Network connectivity to database host")
                raise RuntimeError(f"Database connection failed: {str(e)}")
            logger.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff

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