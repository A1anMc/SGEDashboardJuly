"""Health check endpoints for the application."""

from fastapi import APIRouter
from app.db.session import health_check as check_db_health
from datetime import datetime

router = APIRouter()

@router.get("/")
@router.head("/")
async def health_check():
    db_healthy = check_db_health()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "disconnected",
        "environment": "production",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/db-test")
async def database_test():
    """Detailed database connection test."""
    try:
        from app.db.session import get_engine
        from app.core.config import settings
        
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test, current_database() as db_name, current_user as user")
            row = result.fetchone()
            
        return {
            "status": "success",
            "database": {
                "test": row[0],
                "database_name": row[1],
                "user": row[2],
                "url": settings.DATABASE_URL[:20] + "..." if settings.DATABASE_URL else "not set"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        } 