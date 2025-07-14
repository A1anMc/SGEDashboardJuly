"""Health check endpoints for the application."""

from fastapi import APIRouter
from app.db.session import check_db_health
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