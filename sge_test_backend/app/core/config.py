from typing import List
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "SGE Dashboard API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sge.db")
    TEST_DATABASE_URL: str = "sqlite:///./test.db"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # Next.js development server
        "http://localhost:8000",  # FastAPI development server
    ]

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # JWT
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Scraper
    SCRAPE_CRON_SCHEDULE: str = "0 0 * * *"  # Daily at midnight
    GRANT_SOURCES: List[str] = [
        "https://www.business.gov.au/grants-and-programs",
        "https://www.communitygrants.gov.au/grants"
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 