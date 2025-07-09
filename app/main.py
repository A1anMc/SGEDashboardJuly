"""Main application module."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging_config import setup_logging
from app.core.rate_limiter import ErrorEndpointRateLimiter
from app.api.v1.api import api_router
from app.db.init_db import init_db, check_db_connected

# Set up logging first
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Shadow Goose Entertainment Dashboard API"
)

# Register error handlers
register_exception_handlers(app)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add rate limiter for error endpoints
app.add_middleware(
    ErrorEndpointRateLimiter,
    window_size=60,  # 1 minute window
    max_requests=50  # 50 requests per minute for error endpoints
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    try:
        logger.info("Checking database connection...")
        if not check_db_connected():
            logger.error("Failed to connect to database")
            raise RuntimeError("Database connection failed")
            
        logger.info("Initializing database...")
        if not init_db():
            logger.error("Failed to initialize database")
            raise RuntimeError("Database initialization failed")
            
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Startup failed: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Application shutting down") 