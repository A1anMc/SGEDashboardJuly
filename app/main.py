"""Main application module."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

from app.core.config import settings
from app.core.error_handlers import setup_error_handlers
from app.db.init_db import init_db, check_db_health, get_db_info
from app.api.v1.api import api_router

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events.
    This replaces the @app.on_event("startup") and @app.on_event("shutdown") handlers.
    """
    # Startup: Initialize database with retry logic
    try:
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialization completed")
        
        # Log database info
        db_info = get_db_info()
        logger.info(f"Connected to database: {db_info}")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("Shutting down application...")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Check application and database health."""
        is_healthy = check_db_health()
        if not is_healthy:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "error", "message": "Database connection failed"}
            )
        return {"status": "healthy", "database": "connected"}
    
    # Database info endpoint (protected, for debugging)
    @app.get("/api/debug/db", include_in_schema=False)
    async def db_info():
        """Get database connection information (excluding sensitive data)."""
        if not settings.DEBUG:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "Debug endpoints are only available in debug mode"}
            )
        return get_db_info()
    
    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        """Ensure database is healthy before processing requests."""
        if not request.url.path.startswith(("/health", "/metrics")):
            if not check_db_health():
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={"status": "error", "message": "Database connection lost"}
                )
        response = await call_next(request)
        return response
    
    return app

app = create_app() 