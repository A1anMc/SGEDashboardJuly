import os
from typing import Optional, List, Dict
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from dotenv import load_dotenv

# Load environment variables before creating settings
load_dotenv(".envV2")

class Settings(BaseSettings):
    # Core
    PROJECT_NAME: str = "SGE Dashboard"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENV: str = "development"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "test-key-for-development-only") if not os.getenv("TESTING") else "test-jwt-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sge_dashboard")
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_MAX_RETRIES: int = 5
    DATABASE_RETRY_DELAY: int = 1
    DATABASE_ECHO: bool = False
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    
    # Database Pool Settings
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    DATABASE_CONNECT_TIMEOUT: int = 10
    DATABASE_KEEPALIVES: bool = True
    DATABASE_KEEPALIVES_IDLE: int = 60
    DATABASE_KEEPALIVES_INTERVAL: int = 10
    DATABASE_KEEPALIVES_COUNT: int = 5
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAIL_TEMPLATES_DIR: str = "app/email-templates"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    
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
        }
    }
    
    # External Domain Security
    ALLOWED_EXTERNAL_DOMAINS: List[str] = [
        "business.gov.au",
        "grants.gov.au",
        "arts.gov.au",
        "screenaustralia.gov.au",
        "supabase.co"  # Required for Supabase
    ]
    
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
        
        return v
    
    @field_validator("SUPABASE_URL")
    @classmethod
    def validate_supabase_url(cls, v: str, info) -> str:
        """Validate Supabase URL."""
        if not v and not info.data.get("TESTING", False):
            raise ValueError("SUPABASE_URL is required in non-test environment")
        return v
    
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".envV2",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra fields from environment
    )

# Create settings instance
settings = Settings() 