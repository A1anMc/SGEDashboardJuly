import logging
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import get_db
from app.core.config import settings
from app.db.base import Base

logger = logging.getLogger(__name__)

def init_db():
    """Initialize database with required tables."""
    try:
        with get_db() as db:
            if settings.DATABASE_URL.startswith("postgresql"):
                # Enable PostgreSQL extensions
                db.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"))
                db.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
                db.execute(text("CREATE EXTENSION IF NOT EXISTS hstore;"))
                logger.info("Database extensions initialized successfully")
            
            # Create all tables
            Base.metadata.create_all(bind=db.get_bind())
            logger.info("Database tables created successfully")
            
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def check_db_connected():
    """Check if database is accessible."""
    try:
        with get_db() as db:
            db.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def check_db_tables():
    """Check if all required tables exist."""
    try:
        with get_db() as db:
            # Get list of all tables in database
            inspector = inspect(db.get_bind())
            existing_tables = inspector.get_table_names()
            
            # Get list of all models
            model_tables = Base.metadata.tables.keys()
            
            # Check if any tables are missing
            missing_tables = set(model_tables) - set(existing_tables)
            
            if missing_tables:
                logger.warning(f"Missing tables detected: {missing_tables}")
                return False
            
            logger.info("All required tables exist")
            return True
            
    except Exception as e:
        logger.error(f"Error checking database tables: {str(e)}")
        return False 