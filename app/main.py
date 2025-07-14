"""
Shadow Goose Entertainment API - Production Hardened
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
from app.db.session import get_engine_instance, close_database
from app.core.config import settings
from app.core.error_handlers import setup_error_handlers
from app.db.init_db import init_db, check_db_health, get_db_info, validate_database_config

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
        logger.info(f"Starting Shadow Goose Entertainment API in {settings.ENV} environment")
        logger.info(f"Debug mode: {settings.DEBUG}")
        
        # Security check: Ensure we're not in debug mode in production
        if settings.ENV == 'production' and settings.DEBUG:
            logger.error("DEBUG mode is enabled in production! This is a security risk.")
            raise RuntimeError("DEBUG mode must be disabled in production")
        
        # Validate database configuration first
        logger.info("Validating database configuration...")
        if not validate_database_config():
            error_msg = "Database configuration validation failed. Please check your DATABASE_URL environment variable."
            logger.error(error_msg)
            if settings.ENV == 'production':
                raise RuntimeError(error_msg)
            else:
                logger.warning("Continuing in development mode with database issues")
        
        # Initialize database
        logger.info("Initializing database...")
        try:
            init_db()
            
            # Create tables if they don't exist
            engine = get_engine_instance()
            Base.metadata.create_all(bind=engine)
            logger.info("Database initialization completed")
            
        except Exception as db_error:
            logger.error(f"Database initialization failed: {str(db_error)}")
            if settings.ENV == 'production':
                # In production, we must have a working database
                raise RuntimeError(f"Database initialization failed: {str(db_error)}")
            else:
                # In development, we can continue with warnings
                logger.warning("Continuing in development mode with database issues")
        
        # Log database info (excluding sensitive data in production)
        try:
            if settings.DEBUG:
                db_info = get_db_info()
                logger.info(f"Connected to database: {db_info}")
            else:
                logger.info("Database connection established")
        except Exception as info_error:
            logger.warning(f"Could not retrieve database info: {str(info_error)}")
        
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
    logger.info("Shutting down Shadow Goose Entertainment API...")
    try:
        close_database()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application with comprehensive security."""
    
    # Disable docs in production for security
    docs_url = "/api/docs" if settings.DEBUG else None
    openapi_url = "/api/openapi.json" if settings.DEBUG else None
    
    app = FastAPI(
        title="Shadow Goose Entertainment API",
        description="API for managing Shadow Goose Entertainment projects and resources - Production Hardened",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=docs_url,
        openapi_url=openapi_url,
        # Security: Don't expose server info in production
        servers=[{"url": "/", "description": "SGE API Server"}] if settings.ENV == 'production' else None,
    )
    
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
                f"Request completed",
                extra={
                    "path": path,
                    "method": method,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2)
                }
            )
            
            return response
            
        except Exception as e:
            # Log detailed error information
            logger.error(
                f"Request failed",
                extra={
                    "path": path,
                    "method": method,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "duration_ms": round((time.time() - start_time) * 1000, 2)
                }
            )
            
            # Report to Sentry if available
            if settings.SENTRY_DSN:
                try:
                    import sentry_sdk
                    sentry_sdk.capture_exception(e)
                except ImportError:
                    pass
            
            # Return error response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": str(e) if settings.DEBUG else "Internal server error",
                    "path": path,
                    "method": method
                }
            )
    
    # 2. Trusted Host Middleware (prevent host header attacks)
    if settings.ENV == 'production':
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.TRUSTED_HOSTS
        )
    
    # 2. Session Middleware with secure settings
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="sge_session",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        same_site="lax"
    )
    
    # 3. CORS Middleware (configured from environment)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # 4. Rate Limiting Middleware
    if rate_limiter:
        app.state.limiter = rate_limiter
        app.add_middleware(SlowAPIMiddleware)
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # 5. Security Headers Middleware
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        """Add comprehensive security headers to all responses."""
        response = await call_next(request)
        
        # Security headers for all environments
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Additional security headers for production
        if settings.ENV == 'production':
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
            
            # Enhanced Content Security Policy
            csp_policy = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https:",
                "font-src 'self' data:",
                f"connect-src 'self' {settings.FRONTEND_URL} https://sge-dashboard-web.onrender.com https://sge-dashboard-api.onrender.com",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "object-src 'none'"
            ]
            response.headers["Content-Security-Policy"] = "; ".join(csp_policy)
        
        # Remove server header for security
        if "server" in response.headers:
            del response.headers["server"]
        
        return response
    
    # 6. Database Health Check Middleware
    @app.middleware("http")
    async def db_health_middleware(request: Request, call_next):
        """Ensure database is healthy before processing requests."""
        # Skip health checks to avoid circular dependency
        if not request.url.path.startswith(("/health", "/metrics")):
            try:
                if not check_db_health():
                    logger.error("Database health check failed")
                    return JSONResponse(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        content={"status": "error", "message": "Database connection lost"}
                    )
            except Exception as e:
                logger.error(f"Database health check error: {str(e)}")
                # In development, continue; in production, fail
                if settings.ENV == 'production':
                    return JSONResponse(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        content={"status": "error", "message": "Database health check failed"}
                    )
        
        # Add request timing for monitoring
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    # Setup error handlers
    setup_error_handlers(app)
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    # === ENHANCED ENDPOINTS ===
    
    @app.get("/")
    async def read_root():
        """Root endpoint with rate limiting."""
        if rate_limiter:
            # Rate limiting will be handled by middleware
            pass
        return {
            "message": "Welcome to the Shadow Goose Entertainment API!",
            "version": "1.0.0",
            "environment": settings.ENV,
            "status": "operational"
        }
    

    
    # Debug endpoints (only available in debug mode)
    @app.get("/api/debug/db", include_in_schema=False)
    async def db_info():
        """Get database connection information (excluding sensitive data)."""
        if not settings.DEBUG:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "Debug endpoints are only available in debug mode"}
            )
        return get_db_info()
    
    @app.get("/api/debug/cors", include_in_schema=False)
    async def cors_info():
        """Get CORS configuration info for debugging."""
        return {
            "cors_origins": settings.CORS_ORIGINS,
            "cors_allow_credentials": settings.CORS_ALLOW_CREDENTIALS,
            "cors_allow_methods": settings.CORS_ALLOW_METHODS,
            "cors_allow_headers": settings.CORS_ALLOW_HEADERS,
            "environment": settings.ENV,
            "frontend_url": settings.FRONTEND_URL,
            "debug": settings.DEBUG
        }
    
    @app.get("/api/security/info", include_in_schema=False)
    async def security_info():
        """Get security configuration info (non-sensitive)."""
        if not settings.DEBUG:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"error": "Security info only available in debug mode"}
            )
        
        return {
            "environment": settings.ENV,
            "debug": settings.DEBUG,
            "cors_origins": settings.CORS_ORIGINS,
            "rate_limiting": rate_limiter is not None,
            "sentry_enabled": settings.SENTRY_DSN is not None,
            "trusted_hosts": settings.ENV == 'production',
            "secure_cookies": settings.ENV == 'production',
        }
    
    # Custom rate limit exception handler
    if rate_limiter:
        @app.exception_handler(RateLimitExceeded)
        async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
            """Enhanced rate limit exception handler."""
            logger.warning(f"Rate limit exceeded for {request.client.host}: {exc}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": str(exc.retry_after) if hasattr(exc, 'retry_after') else "60"
                }
            )
    
    logger.info(f"Shadow Goose Entertainment API created successfully in {settings.ENV} mode")
    return app

# Create the application instance
app = create_app() 