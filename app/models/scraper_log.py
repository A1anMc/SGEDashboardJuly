from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from app.db.base_class import Base

class ScraperLog(Base):
    """Model for tracking scraper activity and results."""
    
    __tablename__ = "scraper_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)
    duration_seconds = Column(Integer)
    status = Column(String(50), nullable=False)  # success, error, partial
    grants_found = Column(Integer, default=0)
    grants_added = Column(Integer, default=0)
    grants_updated = Column(Integer, default=0)
    error_message = Column(Text)
    scraper_metadata = Column("metadata", JSON)  # Store additional info like URLs scraped, rate limits, etc.
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = datetime.utcnow()
        
    def complete(self, status: str, grants_found: int = 0, grants_added: int = 0, 
                grants_updated: int = 0, error_message: str = None, metadata: dict = None):
        """Mark the scraping job as complete and calculate duration."""
        self.end_time = datetime.utcnow()
        self.duration_seconds = int((self.end_time - self.start_time).total_seconds())
        self.status = status
        self.grants_found = grants_found
        self.grants_added = grants_added
        self.grants_updated = grants_updated
        self.error_message = error_message
        self.scraper_metadata = metadata or {} 