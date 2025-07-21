import os
from typing import Optional, List, Dict, Union
from dotenv import load_dotenv
import json

# Force environment to production on Render
if os.getenv("RENDER", "false").lower() == "true":
    os.environ["ENVIRONMENT"] = "production"
    print("Render detected - forcing production environment")

# Print environment state before loading anything
print("Initial environment:", os.getenv("ENVIRONMENT", "not set"))
print("Initial DATABASE_URL:", os.getenv("DATABASE_URL", "not set"))

# Only load .env in development
if os.getenv("ENVIRONMENT", "development") != "production":
    try:
        load_dotenv(dotenv_path=".env", override=False)
        print("Loaded .env file (development mode)")
    except Exception as e:
        print(f"Warning: Error loading .env file: {e}")
else:
    print("Production environment detected - skipping .env file loading")

# Print environment state after loading
print("Final environment:", os.getenv("ENVIRONMENT", "not set"))
print("Final DATABASE_URL:", os.getenv("DATABASE_URL", "not set"))

class Settings:
    # Core
    PROJECT_NAME: str = "NavImpact"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENV: str = "production" if os.getenv("RENDER", "false").lower() == "true" else os.getenv("ENVIRONMENT", "development")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "test-key-for-development-only") if not os.getenv("TESTING") else "test-jwt-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://navimpact@localhost:5432/navimpact")
    TEST_DATABASE_URL: str = "postgresql://navimpact@localhost:5432/navimpact_test"
    DATABASE_MAX_RETRIES: int = int(os.getenv("DATABASE_MAX_RETRIES", "5"))
    DATABASE_RETRY_DELAY: int = int(os.getenv("DATABASE_RETRY_DELAY", "1"))
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"
    TESTING: bool = os.getenv("TESTING", "false").lower() == "true"
    
    # Database Pool Settings
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "10"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "60"))
    DATABASE_POOL_RECYCLE: int = int(os.getenv("DATABASE_POOL_RECYCLE", "900"))
    
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
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT")) if os.getenv("SMTP_PORT") else None
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAILS_FROM_EMAIL: Optional[str] = os.getenv("EMAILS_FROM_EMAIL")
    EMAILS_FROM_NAME: Optional[str] = os.getenv("EMAILS_FROM_NAME")
    EMAIL_TEMPLATES_DIR: str = "app/email-templates"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Sentry
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = os.getenv("SENTRY_ENVIRONMENT", "development")
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "false" if os.getenv("ENVIRONMENT", "development") == "development" else "true").lower() == "true"
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100" if os.getenv("ENVIRONMENT", "development") == "development" else "60"))
    RATE_LIMIT_REQUESTS_PER_HOUR: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_HOUR", "10000" if os.getenv("ENVIRONMENT", "development") == "development" else "1000"))
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # Trusted Hosts (for production)
    TRUSTED_HOSTS: List[str] = [
        "navimpact-api.onrender.com",
        "localhost",
        "127.0.0.1"
    ]
    
    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    def __init__(self):
        # Parse CORS origins from environment
        cors_origins_str = os.getenv("CORS_ORIGINS", "")
        if cors_origins_str:
            if isinstance(cors_origins_str, str):
                if cors_origins_str.startswith("["):
                    try:
                        self.CORS_ORIGINS = json.loads(cors_origins_str)
                    except json.JSONDecodeError:
                        self.CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]
                else:
                    self.CORS_ORIGINS = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]
            else:
                self.CORS_ORIGINS = cors_origins_str
        else:
            # Default CORS origins based on environment
            if self.ENV == "production":
                self.CORS_ORIGINS = [
                    "https://navimpact.onrender.com",
                    "https://navimpact-frontend.onrender.com",
                    "https://navimpact-api.onrender.com"
                ]
            else:
                self.CORS_ORIGINS = [
                    "http://localhost:3000",
                    "http://localhost:8000",
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:8000"
                ]

# Create settings instance
settings = Settings() 