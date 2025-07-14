"""Health check endpoints for the application."""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.core.config import settings
from app.db.init_db import get_db_info, check_db_health
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check(response: Response):
    """
    Enhanced health check endpoint with database pool monitoring.
    Does not require database session by default.
    """
    try:
        # Basic database health check
        db_healthy = check_db_health()
        
        # Get database info (without requiring session)
        try:
            db_info = get_db_info()
        except Exception as e:
            logger.warning(f"Could not get database info: {e}")
            db_info = {"error": str(e)}
        
        # Get pool metrics
        pool_metrics = None
        try:
            from app.db.pool_monitor import check_pool_health
            pool_metrics = check_pool_health()
        except Exception as e:
            logger.warning(f"Could not get pool metrics: {e}")
            pool_metrics = {"error": "Pool monitoring unavailable"}
        
        # Get API client metrics
        api_client_metrics = None
        try:
            from app.core.api_client import get_all_client_metrics, health_check_all_clients
            api_client_metrics = {
                "metrics": get_all_client_metrics(),
                "health_checks": health_check_all_clients()
            }
        except Exception as e:
            logger.warning(f"Could not get API client metrics: {e}")
            api_client_metrics = {"error": "API client monitoring unavailable"}
        
        # Overall health status
        overall_status = "healthy"
        if not db_healthy:
            overall_status = "unhealthy"
            response.status_code = 503  # Service Unavailable
        elif pool_metrics and pool_metrics.get("status") == "critical":
            overall_status = "degraded"
            response.status_code = 200  # Still available but degraded
        else:
            response.status_code = 200  # Healthy
        
        health_response = {
            "status": overall_status,
            "database": "connected" if db_healthy else "disconnected",
            "environment": settings.ENV,
            "version": settings.VERSION,
            "timestamp": datetime.now().isoformat(),
            "database_info": db_info,
            "pool_metrics": pool_metrics,
            "api_client_metrics": api_client_metrics
        }
        
        # Add configuration info (without sensitive data)
        health_response["configuration"] = {
            "debug": settings.DEBUG,
            "rate_limiting": settings.RATE_LIMIT_ENABLED,
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": settings.DATABASE_POOL_TIMEOUT
        }
        
        return health_response
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        response.status_code = 503  # Service Unavailable
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "environment": settings.ENV,
            "version": settings.VERSION
        } 