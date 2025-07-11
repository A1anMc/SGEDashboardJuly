import os
from typing import Optional, List, Dict, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from dotenv import load_dotenv
import json

# Load environment variables before creating settings
load_dotenv(dotenv_path=".envV2", override=True)

class Settings(BaseSettings):
    # Core
    PROJECT_NAME: str = "SGE Dashboard"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENV: str = os.getenv("ENVIRONMENT", "development")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "test-key-for-development-only") if not os.getenv("TESTING") else "test-jwt-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://alanmccarthy@localhost:5432/sge_dashboard")
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_MAX_RETRIES: int = int(os.getenv("DATABASE_MAX_RETRIES", "5"))
    DATABASE_RETRY_DELAY: int = int(os.getenv("DATABASE_RETRY_DELAY", "1"))
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    
    # Database Pool Settings
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
    DATABASE_POOL_RECYCLE: int = int(os.getenv("DATABASE_POOL_RECYCLE", "1800"))  # 30 minutes
    
    # CORS Settings - Environment-based configuration
    CORS_ORIGINS: List[str] = []
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = [
        "GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"
    ]
    CORS_ALLOW_HEADERS: List[str] = [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "X-CSRF-Token"
    ]
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else None
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")  # From environment only
    EMAILS_FROM_EMAIL: Optional[str] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = os.getenv("EMAILS_FROM_NAME")
    EMAIL_TEMPLATES_DIR: str = "app/email-templates"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Sentry - Only from environment variables
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", "development")
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
    RATE_LIMIT_REQUESTS_PER_HOUR: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "1000"))
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")  # For rate limiting backend
    
    # Trusted Hosts (for production)
    TRUSTED_HOSTS: List[str] = [
        "sge-dashboard-api.onrender.com",
        "localhost",
        "127.0.0.1"
    ]
    
    # Frontend URL (for CORS and security)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # Scraper Configuration
    ALLOWED_SCRAPER_SOURCES: Dict[str, Dict[str, str]] = {
        "business.gov.au": {
            "base_url": "https://business.gov.au",
            "grants_path": "/grants-and-programs",
            "description": "Australian Government Business Grants"
        },
        "grants.gov.au": {
            "base_url": "https://www.grants.gov.au",
            "api_path": "/api/v1/grants",
            "description": "GrantConnect Portal"
        },
        "arts.gov.au": {
            "base_url": "https://www.arts.gov.au",
            "grants_path": "/funding-and-support",
            "description": "Australian Arts Grants"
        },
        "screenaustralia.gov.au": {
            "base_url": "https://www.screenaustralia.gov.au",
            "grants_path": "/funding-and-support",
            "description": "Screen Australia Funding"
        },
        "australian_grants": {
            "base_url": "https://www.screenaustralia.gov.au",  # Default to Screen Australia as primary source
            "grants_path": "/funding-and-support",
            "description": "Australian Grants Aggregator"
        }
    }
    
    # External Domain Security
    ALLOWED_EXTERNAL_DOMAINS: List[str] = [
        "business.gov.au",
        "grants.gov.au",
        "arts.gov.au",
        "screenaustralia.gov.au",
        "supabase.co",  # Required for Supabase
        "create.nsw.gov.au"  # Added for NSW state grants
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def validate_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Validate and parse CORS origins from environment."""
        if isinstance(v, str):
            # Handle JSON string from environment variable
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                # Handle comma-separated string
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        
        # Default CORS origins based on environment
        env = os.getenv("ENVIRONMENT", "development")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        if env == "production":
            return [
                frontend_url,
                "https://sge-dashboard-web.onrender.com",
                "https://sge-dashboard-api.onrender.com"
            ]
        else:
            return [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000"
            ]
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Ensure secret key is secure in production."""
        env = info.data.get("ENV", "development")
        if env == "production" and v == "your-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be changed from default value in production")
        if env == "production" and len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v
    
    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str, info) -> str:
        """Validate database URL based on environment."""
        # If we're testing, use the test database URL
        if info.data.get("TESTING", False):
            return info.data.get("TEST_DATABASE_URL", "sqlite:///./test.db")
        
        # For SQLite URLs, no further validation needed
        if v.startswith("sqlite:///"):
            return v
        
        # For PostgreSQL URLs, basic validation
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must start with postgresql:// or sqlite:///")
        
        # For Supabase URLs, ensure proper format
        if "supabase.co" in v:
            # Add application name for better monitoring
            if "application_name" not in v:
                v = f"{v}?application_name=sge-dashboard-api"
            # Add SSL mode if not specified
            if "sslmode" not in v:
                v = f"{v}&sslmode=require"
        
        return v
    
    @field_validator("SUPABASE_URL")
    @classmethod
    def validate_supabase_url(cls, v: str, info) -> str:
        """Validate Supabase URL."""
        if not v and not info.data.get("TESTING", False):
            return ""  # Allow empty Supabase URL in development
        return v
    
    @field_validator("DEBUG")
    @classmethod
    def validate_debug_mode(cls, v: bool, info) -> bool:
        """Ensure debug is disabled in production."""
        env = info.data.get("ENV", "development")
        if env == "production" and v:
            # Log warning but don't fail - let the app handle this
            import logging
            logging.warning("DEBUG mode should be disabled in production")
        return v
    
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".envV2",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from environment
    )

# Create settings instance
settings = Settings() 