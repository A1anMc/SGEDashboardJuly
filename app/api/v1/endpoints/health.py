"""Health check endpoints for the application."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timezone

from app.core.deps import get_db
from app.db.session import check_db_health
from app.core.error_handlers import get_error_stats

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check with system status and error monitoring."""
    
    # Get database health status
    db_healthy = check_db_health()
    
    # Get error statistics
    error_stats = get_error_stats()
    
    # Calculate error rate (errors in last 24h)
    error_count = error_stats.get("error_count_24h", 0)
    
    # Get last error information
    last_error = {
        "timestamp": error_stats.get("last_error_timestamp"),
        "type": error_stats.get("last_error_type")
    } if error_stats.get("last_error_timestamp") else None
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "last_checked": datetime.now(timezone.utc).isoformat()
            }
        },
        "error_monitoring": {
            "error_count_24h": error_count,
            "last_error": last_error
        }
    } 