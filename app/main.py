"""
NavImpact API - Production Ready
Enhanced with comprehensive security measures for production deployment.
"""

from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
import logging
import time
import os
import sys
import traceback

# Import Base and models
from app.db.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.team_member import TeamMember  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.metric import Metric  # noqa: F401
from app.models.program_logic import ProgramLogic  # noqa: F401
from app.models.grant import Grant  # noqa: F401
from app.models.task import Task  # noqa: F401
from app.models.task_comment import TaskComment  # noqa: F401
from app.models.time_entry import TimeEntry  # noqa: F401

from app.api.v1.api import api_router
from app.db.session import get_engine, close_database
from app.core.config import settings
from app.core.error_handlers import setup_error_handlers
from app.db.init_db import init_db, get_db_info, validate_database_config

# Configure logging with production-safe format
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Initialize Sentry for error tracking in production
if settings.SENTRY_DSN and settings.ENV == 'production':
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                FastApiIntegration(auto_enable=True),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            environment=settings.SENTRY_ENVIRONMENT,
            send_default_pii=False,  # Don't send PII in production
            profiles_sample_rate=1.0 if settings.ENV == 'production' else 0.0,
        )
        logger.info("Sentry initialized for error tracking")
    except ImportError:
        logger.warning("Sentry SDK not installed, skipping error tracking setup")

# Rate limiting setup (enhanced SlowAPI configuration)
rate_limiter = None
if settings.ENV == 'production' and settings.RATE_LIMIT_ENABLED:
    try:
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        from slowapi.middleware import SlowAPIMiddleware
        
        # Create rate limiter with configurable limits
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[
                f"{settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/minute",
                f"{settings.RATE_LIMIT_REQUESTS_PER_HOUR}/hour"
            ],
            storage_uri=settings.REDIS_URL or "memory://",
        )
        rate_limiter = limiter
        logger.info(f"Rate limiting enabled: {settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/min, {settings.RATE_LIMIT_REQUESTS_PER_HOUR}/hour")
    except ImportError:
        logger.warning("SlowAPI not installed, rate limiting disabled")
else:
    logger.info(f"Rate limiting disabled in {settings.ENV} environment")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events with enhanced error handling.
    """
    # Startup: Initialize database and security checks
    try:
        logger.info(f"Starting NavImpact API in {settings.ENV} environment")
        logger.info(f"Debug mode: {settings.DEBUG}")
        
        # Security check: Ensure we're not in debug mode in production
        if settings.ENV == 'production' and settings.DEBUG:
            logger.error("DEBUG mode is enabled in production! This is a security risk.")
            raise RuntimeError("DEBUG mode must be disabled in production")
        
        # Initialize database
        logger.info("Initializing database...")
        engine = get_engine()
        app.state.engine = engine
        init_db()
        logger.info("Database initialized successfully.")
        
        # Validate database configuration
        logger.info("Validating database configuration...")
        validate_database_config()
        logger.info("Database configuration validated.")
        
        # Check database health
        logger.info("Checking database health...")
        from app.db.session import health_check
        if health_check():
            logger.info("Database health check passed.")
        else:
            logger.warning("Database health check failed.")
        
        # Error handlers are set up during app creation, not during startup
        logger.info("Application startup completed successfully.")
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        # Report to Sentry if available
        if settings.SENTRY_DSN:
            try:
                import sentry_sdk
                sentry_sdk.capture_exception(e)
            except ImportError:
                pass
        raise
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("Shutting down NavImpact API...")
    try:
        close_database()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application with comprehensive security."""
    
    # Enable docs for testing and development
    docs_url = "/docs"
    openapi_url = "/openapi.json"
    
    app = FastAPI(
        title="NavImpact API",
        description="API for managing NavImpact projects and resources - Production Ready",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=docs_url,
        openapi_url=openapi_url,
        servers=[{"url": "/", "description": "NavImpact API Server"}] if settings.ENV == 'production' else None,
    )
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # === SECURITY MIDDLEWARE STACK (Order matters!) ===
    
    # 1. Error Logging Middleware (must be first to catch all errors)
    @app.middleware("http")
    async def error_logging_middleware(request: Request, call_next):
        """Log detailed error information in production."""
        start_time = time.time()
        path = request.url.path
        method = request.method
        
        try:
            response = await call_next(request)
            
            # Log response time for all requests
            duration = time.time() - start_time
            logger.info(
                f"{method} {path} - {response.status_code} - {duration:.3f}s"
            )
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"{method} {path} - ERROR - {duration:.3f}s - {str(e)}"
            )
            # Re-raise the exception
            raise
    
    # 2. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # 3. Trusted Host Middleware (for production)
    if settings.ENV == 'production':
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.TRUSTED_HOSTS
        )
    
    # 4. Security Headers Middleware
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        """Add security headers to all responses."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS header (HTTPS only)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Content Security Policy
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response
    
    # 5. Rate Limiting Middleware (if enabled)
    if rate_limiter:
        app.state.limiter = rate_limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
        app.add_middleware(SlowAPIMiddleware)
    
    # === ROUTES ===
    
    @app.get("/")
    async def read_root():
        """Root endpoint with basic information."""
        return {
            "message": "NavImpact API",
            "version": "1.0.0",
            "environment": settings.ENV,
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        try:
            # Check database health using the correct function
            from app.db.session import health_check as check_db_health
            db_healthy = check_db_health()
            
            return {
                "status": "healthy",
                "database": "connected" if db_healthy else "disconnected",
                "timestamp": datetime.utcnow().isoformat(),
                "environment": settings.ENV,
                "version": "1.0.0"
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    return app

# Create the app
app = create_app() 