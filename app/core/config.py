import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SGE Dashboard"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",     # Next.js development server
        "http://127.0.0.1:3000",     # Next.js alternative local URL
        "http://localhost:5173",     # Vite default port
        "http://127.0.0.1:5173",     # Vite alternative local URL
        "https://dashboard.shadowgoose.com",  # Production frontend
        "https://*.vercel.app"       # Vercel preview deployments
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    # JWT Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-testing")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Email Configuration
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "test@example.com")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "test_password")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "test@example.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.mailtrap.io")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "SGE Dashboard")
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False
    USE_CREDENTIALS: bool = True
    
    # Frontend URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    DASHBOARD_URL: str = os.getenv("DASHBOARD_URL", "http://localhost:3000/dashboard")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/app.log"
    
    # Supabase Configuration
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Airtable Configuration
    AIRTABLE_API_KEY: str = os.getenv("AIRTABLE_API_KEY", "")
    AIRTABLE_BASE_ID: str = os.getenv("AIRTABLE_BASE_ID", "")
    
    # External APIs Configuration
    BUSINESS_GOV_API_KEY: str = os.getenv("BUSINESS_GOV_API_KEY", "")
    GRANTS_GOV_API_KEY: str = os.getenv("GRANTS_GOV_API_KEY", "")
    
    # SendGrid Configuration
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@shadowgoose.com")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Shadow Goose Entertainment")
    
    model_config = SettingsConfigDict(case_sensitive=True)

settings = Settings() 