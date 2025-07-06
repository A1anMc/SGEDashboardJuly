import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Environment
    ENV: str = os.getenv("ENV", "development")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SGE Dashboard"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = []
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set CORS origins based on environment or environment variable
        if not self.CORS_ORIGINS:
            cors_env = os.getenv("CORS_ORIGINS", "")
            if cors_env:
                # Parse comma-separated string from environment
                self.CORS_ORIGINS = [origin.strip() for origin in cors_env.split(",") if origin.strip()]
            else:
                # Default origins based on environment
                if self.ENV == "production":
                    self.CORS_ORIGINS = [
                        "https://sge-dashboard.onrender.com",
                        "https://*.onrender.com"
                    ]
                else:
                    self.CORS_ORIGINS = [
                        "http://localhost:3000",
                        "http://127.0.0.1:3000"
                    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Security Configuration
    SECURITY_HEADERS: bool = ENV == "production"
    RATE_LIMIT_PER_SECOND: int = int(os.getenv("RATE_LIMIT_PER_SECOND", "10"))
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SECURE: bool = ENV == "production"
    SESSION_COOKIE_SAMESITE: str = "Lax"
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///app.db")
    # Render Postgres Optimizations
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))  # Reduced for Render
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    DATABASE_POOL_TIMEOUT: int = int(os.getenv("DATABASE_POOL_TIMEOUT", "30"))
    DATABASE_POOL_RECYCLE: int = int(os.getenv("DATABASE_POOL_RECYCLE", "1800"))  # 30 minutes
    DATABASE_ECHO: bool = ENV == "development"
    DATABASE_SSL_REQUIRED: bool = ENV == "production"
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    if not SECRET_KEY and ENV == "production":
        raise ValueError("SECRET_KEY environment variable is required in production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Monitoring Configuration
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = ENV
    SENTRY_TRACES_SAMPLE_RATE: float = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))
    
    # Email Configuration (SendGrid)
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@shadowgoose.com")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Shadow Goose Entertainment")
    
    # Frontend URLs
    FRONTEND_URL: str = os.getenv(
        "FRONTEND_URL",
        "https://sge-dashboard-web.onrender.com" if ENV == "production" else "http://localhost:3000"
    )
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_JSON: bool = ENV == "production"  # Use JSON logging in production
    
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings() 