"""Health check endpoints for the application."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import deps
from app.db.session import engine
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2025-07-22T06:00:00.000000",
        "environment": "production",
        "version": "1.0.0"
    }

@router.get("/db-test")
def database_test():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            row = result.fetchone()
            
            # Get database info
            db_info = conn.execute("SELECT current_database() as db_name, current_user as db_user")
            db_row = db_info.fetchone()
            
            return {
                "status": "success",
                "database": {
                    "test": row[0],
                    "database_name": db_row[0],
                    "user": db_row[1],
                    "url": str(engine.url).replace(str(engine.url.password), "***") if engine.url.password else str(engine.url)
                },
                "timestamp": "2025-07-22T06:00:00.000000"
            }
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "traceback": str(e.__traceback__),
            "timestamp": "2025-07-22T06:00:00.000000"
        }

@router.get("/session-test")
def session_test(db: Session = Depends(deps.get_db)):
    """Test database session."""
    try:
        result = db.execute("SELECT 1 as test")
        row = result.fetchone()
        return {
            "status": "success",
            "session_test": row[0],
            "timestamp": "2025-07-22T06:00:00.000000"
        }
    except Exception as e:
        logger.error(f"Session test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-migration")
def run_migration():
    """Temporary endpoint to run database migrations."""
    try:
        from alembic import command
        from alembic.config import Config
        
        # Create Alembic config
        alembic_cfg = Config("alembic.ini")
        
        # Run migration
        command.upgrade(alembic_cfg, "head")
        
        return {
            "status": "success",
            "message": "Migration completed successfully",
            "timestamp": "2025-07-22T06:00:00.000000"
        }
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-07-22T06:00:00.000000"
        } 