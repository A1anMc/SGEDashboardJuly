"""Main application module."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.error_handlers import register_exception_handlers
from app.core.logging_config import setup_logging
from app.core.rate_limiter import ErrorEndpointRateLimiter
from app.db.session import get_db_session
from app.db.init_db import init_db, check_db_health
from app.api.v1.api import api_router

# Set up logging first
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    # Startup
    setup_logging()
    if not check_db_health():
        raise RuntimeError("Failed to connect to database")
    if not init_db():
        raise RuntimeError("Failed to initialize database")
    
    yield
    
    # Shutdown
    # Add any cleanup code here
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
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

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check application health."""
    return {
        "status": "healthy",
        "database": check_db_health(),
        "version": settings.VERSION
    } 