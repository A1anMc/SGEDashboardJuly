import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment
TESTING = os.getenv("TESTING", "false").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sge_dashboard")
TEST_DATABASE_URL = "sqlite:///./test.db"

# Use test database if in test environment
SQLALCHEMY_DATABASE_URL = TEST_DATABASE_URL if TESTING else DATABASE_URL

# Configure engine based on database type
if SQLALCHEMY_DATABASE_URL.startswith("sqlite:"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True,
        connect_args={
            "connect_timeout": 10,
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
    )

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if settings.TESTING:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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

# Log database connection status
# The original code had this listener, but the new code doesn't explicitly manage the engine instance.
# Assuming the intent was to keep the listener if the engine is still managed, but the new code
# doesn't expose the engine directly. For now, I'll remove the listener as the engine is no longer
# directly accessible in the new_code's SessionLocal context.
# @event.listens_for(Engine, "connect")
# def receive_connect(dbapi_connection, connection_record):
#     """Log when a connection is created."""
#     logger.info("Database connection established successfully") 