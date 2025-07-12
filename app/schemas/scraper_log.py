from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel

class ScraperLogBase(BaseModel):
    source_name: str
    status: str
    grants_found: int = 0
    grants_added: int = 0
    grants_updated: int = 0
    error_message: Optional[str] = None
    scraper_metadata: Optional[Dict] = None

class ScraperLogCreate(ScraperLogBase):
    pass

class ScraperLogUpdate(ScraperLogBase):
    pass

class ScraperLog(ScraperLogBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None

    class Config:
        from_attributes = True 