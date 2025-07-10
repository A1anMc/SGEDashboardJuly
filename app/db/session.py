import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use SQLite by default
SQLALCHEMY_DATABASE_URL = "sqlite:///./dev.db"

# Configure engine for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
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