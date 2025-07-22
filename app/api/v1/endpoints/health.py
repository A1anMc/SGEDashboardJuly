"""Health check endpoints for the application."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import deps
from app.db.session import get_engine
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "production",
        "version": "1.0.0"
    }

@router.get("/db-test")
def database_test():
    """Test database connection."""
    try:
        engine = get_engine()
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
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
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
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Session test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 