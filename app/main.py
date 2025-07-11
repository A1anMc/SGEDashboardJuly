"""Main application module."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
import logging
import time
import os

from app.core.config import settings
from app.core.error_handlers import setup_error_handlers
from app.db.init_db import init_db, check_db_health, get_db_info
from app.api.v1.api import api_router

# Configure logging with production-safe format
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        # Add file handler in production if needed
        # logging.FileHandler('app.log') if settings.ENV == 'production' else logging.StreamHandler()
    ]
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
            # Don't send PII in production
            send_default_pii=False,
            # Capture 100% of transactions for performance monitoring
            profiles_sample_rate=1.0 if settings.ENV == 'production' else 0.0,
        )
        logger.info("Sentry initialized for error tracking")
    except ImportError:
        logger.warning("Sentry SDK not installed, skipping error tracking setup")

# Rate limiting setup (optional SlowAPI middleware)
rate_limiter = None
if settings.ENV == 'production':
    try:
        from slowapi import Limiter, _rate_limit_exceeded_handler
        from slowapi.util import get_remote_address
        from slowapi.errors import RateLimitExceeded
        
        # Create rate limiter with Redis backend if available, otherwise in-memory
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["60/minute", "1000/hour"],  # Basic rate limiting
            storage_uri=os.getenv("REDIS_URL", "memory://"),  # Use Redis if available
        )
        rate_limiter = limiter
        logger.info("Rate limiting enabled for production")
    except ImportError:
        logger.warning("SlowAPI not installed, rate limiting disabled")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events.
    This replaces the @app.on_event("startup") and @app.on_event("shutdown") handlers.
    """
    # Startup: Initialize database with retry logic
    try:
        logger.info(f"Starting application in {settings.ENV} environment")
        logger.info(f"Debug mode: {settings.DEBUG}")
        
        # Security check: Ensure we're not in debug mode in production
        if settings.ENV == 'production' and settings.DEBUG:
            logger.error("DEBUG mode is enabled in production! This is a security risk.")
            raise RuntimeError("DEBUG mode must be disabled in production")
        
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialization completed")
        
        # Log database info (excluding sensitive data)
        if settings.DEBUG:
            db_info = get_db_info()
            logger.info(f"Connected to database: {db_info}")
        else:
            logger.info("Database connection established")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
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
    logger.info("Shutting down application...")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Disable docs in production for security
    docs_url = "/api/docs" if settings.DEBUG else None
    openapi_url = "/api/openapi.json" if settings.DEBUG else None
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
        docs_url=docs_url,
        openapi_url=openapi_url,
        # Security: Don't expose server info in production
        servers=[{"url": "/", "description": "Current server"}] if settings.ENV == 'production' else None,
    )
    
    # Security Middleware - Order matters!
    
    # 1. Trusted Host Middleware (prevent host header attacks)
    if settings.ENV == 'production':
        trusted_hosts = [
            "sge-dashboard-api.onrender.com",
            "localhost",  # For health checks
            "127.0.0.1",  # For health checks
        ]
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=trusted_hosts
        )
    
    # 2. Session Middleware with secure settings
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie="sge_session",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Match JWT expiry
        # Security: Secure session cookies in production
        same_site="lax" if settings.ENV == 'production' else "lax",
        https_only=settings.ENV == 'production',
        httponly=True,  # Prevent XSS attacks
    )
    
    # 3. CORS Middleware (configured from environment)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # 4. Security Headers Middleware
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        """Add security headers to all responses."""
        response = await call_next(request)
        
        # Security headers for production
        if settings.ENV == 'production':
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
            response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
            
            # Content Security Policy
            csp_policy = [
                "default-src 'self'",
                "script-src 'self'",
                "style-src 'self' 'unsafe-inline'",  # Allow inline styles for FastAPI docs
                "img-src 'self' data: https:",
                "font-src 'self' data:",
                "connect-src 'self' https://sge-dashboard-web.onrender.com",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "object-src 'none'",
                "upgrade-insecure-requests"
            ]
            response.headers["Content-Security-Policy"] = "; ".join(csp_policy)
        
        # Remove server header for security
        response.headers.pop("server", None)
        
        return response
    
    # 5. Rate Limiting Middleware (if available)
    if rate_limiter:
        app.state.limiter = rate_limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # 6. Database Health Check Middleware
    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next):
        """Ensure database is healthy before processing requests."""
        # Skip health checks to avoid circular dependency
        if not request.url.path.startswith(("/health", "/metrics")):
            if not check_db_health():
                logger.error("Database health check failed")
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={"status": "error", "message": "Database connection lost"}
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
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Health check endpoint with rate limiting
    @app.get("/health")
    async def health_check():
        """Check application and database health."""
        # Apply rate limiting in production
        if rate_limiter:
            # This will be handled by the rate limiter middleware
            pass
        
        is_healthy = check_db_health()
        if not is_healthy:
            logger.warning("Health check failed: Database connection issue")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "error", 
                    "message": "Database connection failed",
                    "timestamp": time.time()
                }
            )
        
        return {
            "status": "healthy", 
            "database": "connected",
            "environment": settings.ENV,
            "version": settings.VERSION,
            "timestamp": time.time()
        }
    
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
    
    # Security info endpoint (for security verification)
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
    
    logger.info(f"Application created successfully in {settings.ENV} mode")
    return app

app = create_app() 