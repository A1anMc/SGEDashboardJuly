import logging
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import get_db, check_db_health
from app.core.config import settings
from app.db.base import Base
import time

logger = logging.getLogger(__name__)

def wait_for_db(timeout: int = 60) -> bool:
    """Wait for database to become available."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_db_health():
            return True
        logger.warning(f"Database not ready, waiting {settings.DATABASE_RETRY_DELAY} seconds...")
        time.sleep(settings.DATABASE_RETRY_DELAY)
    return False

def init_db() -> bool:
    """Initialize database with required tables."""
    try:
        # Wait for database to be ready
        if not wait_for_db():
            logger.error("Database not available after timeout")
            return False

        with get_db() as db:
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
            
            # Create all tables
            Base.metadata.create_all(bind=db.get_bind())
            logger.info("Database tables created successfully")
            
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

def check_db_connected() -> bool:
    """Check if database is accessible with detailed diagnostics."""
    try:
        with get_db() as db:
            # Basic connection test
            db.execute(text("SELECT 1"))
            
            # Get PostgreSQL version
            version = db.execute(text("SHOW server_version;")).scalar()
            logger.info(f"Connected to PostgreSQL version: {version}")
            
            # Get current connections
            connections = db.execute(text("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE datname = current_database();
            """)).scalar()
            logger.info(f"Current database connections: {connections}")
            
            # Check transaction status
            idle_transactions = db.execute(text("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE datname = current_database() 
                AND state = 'idle in transaction';
            """)).scalar()
            if idle_transactions > 0:
                logger.warning(f"Found {idle_transactions} idle transactions")
            
            logger.info("Database connection test successful")
            return True
            
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        return False

def check_db_tables() -> bool:
    """Check if all required tables exist with detailed validation."""
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
            
            # Validate table structure
            for table_name in existing_tables:
                if table_name in model_tables:
                    columns = inspector.get_columns(table_name)
                    logger.info(f"Table {table_name} has {len(columns)} columns")
                    
                    # Check primary keys
                    pk = inspector.get_pk_constraint(table_name)
                    if not pk['constrained_columns']:
                        logger.warning(f"Table {table_name} has no primary key")
                    
                    # Check foreign keys
                    fks = inspector.get_foreign_keys(table_name)
                    logger.info(f"Table {table_name} has {len(fks)} foreign key constraints")
            
            logger.info("All required tables exist and are properly structured")
            return True
            
    except Exception as e:
        logger.error(f"Error checking database tables: {str(e)}")
        return False 