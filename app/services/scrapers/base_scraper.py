from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from bs4 import BeautifulSoup
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import verify_external_request
from app.core.config import settings
from app.models.grant import Grant

# Configure logging
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base class for all grant scrapers."""
    
    def __init__(self, db_session: Session, source_id: str):
        """Initialize the scraper with a database session and source ID."""
        if source_id not in settings.ALLOWED_SCRAPER_SOURCES:
            raise ValueError(f"Invalid scraper source: {source_id}")
        
        self.db = db_session
        self.source_id = source_id
        self.source_config = settings.ALLOWED_SCRAPER_SOURCES[source_id]
        self.base_url = self.source_config["base_url"]
    
    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        """Scrape grants from the source. Must be implemented by subclasses."""
        pass
    
    def normalize_grant_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize grant data to a standard format."""
        normalized = {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "source_url": data.get("source_url", ""),
            "open_date": self._parse_date(data.get("open_date")),
            "deadline": self._parse_date(data.get("deadline")),
            "min_amount": data.get("min_amount"),
            "max_amount": data.get("max_amount"),
            "contact_email": data.get("contact_email", ""),
            "industry_focus": data.get("industry_focus", "other"),
            "location": data.get("location", "national"),
            "org_types": data.get("org_types", []),
            "funding_purpose": data.get("funding_purpose", []),
            "audience_tags": data.get("audience_tags", [])
        }
        
        # Clean text fields
        for field in ["title", "description", "contact_email"]:
            if normalized[field]:
                normalized[field] = self._clean_text(normalized[field])
        
        return normalized
    
    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[str]:
        """Make a verified request to an external URL."""
        try:
            response = await verify_external_request(url, method, **kwargs)
            if response and response.status == 200:
                return await response.text()
            else:
                logger.error(f"Error fetching {url}: Status {response.status if response else 'No response'}")
                return None
        except Exception as e:
            logger.error(f"Error making request to {url}: {str(e)}")
            return None
    
    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content safely."""
        try:
            return BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error parsing grant data"
            )
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        return " ".join(text.split())
    
    def _parse_date(self, date_input) -> Optional[datetime]:
        """Parse date string or datetime object into datetime object."""
        if not date_input:
            return None
        
        # If it's already a datetime object, return it
        if isinstance(date_input, datetime):
            return date_input
        
        # If it's not a string, try to convert it
        if not isinstance(date_input, str):
            try:
                date_str = str(date_input)
            except:
                logger.warning(f"Could not convert date input to string: {date_input}")
                return None
        else:
            date_str = date_input
            
        date_formats = [
            "%Y-%m-%d",  # 2024-03-20
            "%d/%m/%Y",  # 20/03/2024
            "%d-%m-%Y",  # 20-03-2024
            "%Y/%m/%d",  # 2024/03/20
            "%d %b %Y",  # 20 Mar 2024
            "%d %B %Y",  # 20 March 2024
            "%B %d, %Y"  # March 20, 2024
        ]
        
        for date_format in date_formats:
            try:
                return datetime.strptime(date_str.strip(), date_format)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _validate_grant_data(self, data: Dict[str, Any]) -> bool:
        """Validate grant data before saving."""
        required_fields = ["title", "description", "source_url"]
        return all(data.get(field) for field in required_fields)
    
    async def save_grants(self, grants: List[Dict[str, Any]]) -> List[Grant]:
        """Save scraped grants to the database."""
        saved_grants = []
        for grant_data in grants:
            if not self._validate_grant_data(grant_data):
                logger.warning(f"Invalid grant data from {self.source_id}: {grant_data}")
                continue
            
            try:
                grant = Grant(
                    source=self.source_id,
                    **grant_data
                )
                self.db.add(grant)
                saved_grants.append(grant)
            except Exception as e:
                logger.error(f"Error saving grant from {self.source_id}: {str(e)}")
                continue
        
        try:
            self.db.commit()
            return saved_grants
        except Exception as e:
            logger.error(f"Error committing grants to database: {str(e)}")
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error saving grants to database"
            ) 