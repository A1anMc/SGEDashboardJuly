from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from app.models.grant import Grant, IndustryFocus, LocationEligibility, OrgType

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base class for all grant scrapers."""
    
    def __init__(self, db: Session, source_name: str):
        self.db = db
        self.source_name = source_name
        
    @abstractmethod
    async def scrape(self) -> List[Dict]:
        """
        Implement this method in each scraper to return a list of grant dictionaries.
        Must return normalized grant data matching our schema.
        """
        pass
    
    def normalize_grant_data(self, raw_data: Dict) -> Dict:
        """
        Normalize raw grant data to match our schema.
        Handles missing fields and data type conversion.
        """
        try:
            return {
                "title": raw_data.get("title", "").strip(),
                "description": raw_data.get("description", "").strip(),
                "source": self.source_name,
                "source_url": raw_data.get("source_url"),
                "industry_focus": self._normalize_industry(raw_data.get("industry_focus")),
                "location_eligibility": self._normalize_location(raw_data.get("location")),
                "org_type_eligible": self._normalize_org_types(raw_data.get("org_types", [])),
                "funding_purpose": raw_data.get("funding_purpose", []),
                "audience_tags": raw_data.get("audience_tags", []),
                "open_date": self._parse_date(raw_data.get("open_date")),
                "deadline": self._parse_date(raw_data.get("deadline")),
                "min_amount": raw_data.get("min_amount"),
                "max_amount": raw_data.get("max_amount"),
                "application_url": raw_data.get("application_url"),
                "contact_email": raw_data.get("contact_email"),
                "notes": raw_data.get("notes"),
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Error normalizing grant data: {str(e)}")
            raise
    
    def save_grants(self, grants: List[Dict]) -> None:
        """
        Save normalized grant data to database.
        Updates existing grants or creates new ones.
        """
        try:
            for grant_data in grants:
                # Validate required fields
                if not all(grant_data.get(field) for field in ["title", "description", "source"]):
                    logger.warning(f"Skipping grant due to missing required fields: {grant_data.get('title', 'Unknown')}")
                    continue
                
                existing = self.db.query(Grant).filter(
                    Grant.source == self.source_name,
                    Grant.application_url == grant_data.get("application_url")
                ).first()
                
                if existing:
                    # Update existing grant
                    for key, value in grant_data.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                    logger.info(f"Updated existing grant: {existing.title}")
                else:
                    # Create new grant
                    grant = Grant(**grant_data)
                    self.db.add(grant)
                    logger.info(f"Created new grant: {grant_data['title']}")
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error saving grants: {str(e)}")
            self.db.rollback()
            raise
    
    def _normalize_industry(self, industry: Optional[str]) -> IndustryFocus:
        """Map source-specific industry to our IndustryFocus enum."""
        industry_map = {
            "media": IndustryFocus.MEDIA,
            "film": IndustryFocus.MEDIA,
            "television": IndustryFocus.MEDIA,
            "digital media": IndustryFocus.MEDIA,
            "arts": IndustryFocus.CREATIVE_ARTS,
            "creative": IndustryFocus.CREATIVE_ARTS,
            "culture": IndustryFocus.CREATIVE_ARTS
        }
        if not industry:
            return IndustryFocus.OTHER
        
        normalized = industry.lower().strip()
        return industry_map.get(normalized, IndustryFocus.OTHER)
    
    def _normalize_location(self, location: Optional[str]) -> LocationEligibility:
        """Map source-specific location to our LocationEligibility enum."""
        location_map = {
            "national": LocationEligibility.NATIONAL,
            "australia": LocationEligibility.NATIONAL,
            "vic": LocationEligibility.VIC,
            "victoria": LocationEligibility.VIC,
            "nsw": LocationEligibility.NSW,
            "new south wales": LocationEligibility.NSW,
            # Add other states as needed
        }
        if not location:
            return LocationEligibility.NATIONAL
            
        normalized = location.lower().strip()
        return location_map.get(normalized, LocationEligibility.OTHER)
    
    def _normalize_org_types(self, org_types: List[str]) -> List[OrgType]:
        """Map source-specific org types to our OrgType enum."""
        org_type_map = {
            "social enterprise": OrgType.SOCIAL_ENTERPRISE,
            "not for profit": OrgType.NFP,
            "nfp": OrgType.NFP,
            "small business": OrgType.SME,
            "sme": OrgType.SME,
            "startup": OrgType.STARTUP,
            "any": OrgType.ANY
        }
        
        normalized = []
        for org_type in org_types:
            if not org_type:
                continue
            mapped = org_type_map.get(org_type.lower().strip())
            if mapped:
                normalized.append(mapped)
        
        return normalized if normalized else [OrgType.ANY]
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date string to datetime.
        Handles common date formats.
        """
        if not date_str:
            return None
            
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None 