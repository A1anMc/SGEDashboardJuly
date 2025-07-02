import aiohttp
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class GrantConnectScraper(BaseScraper):
    """Scraper for GrantConnect (grantconnect.gov.au)."""
    
    BASE_URL = "https://www.grants.gov.au"
    SEARCH_URL = f"{BASE_URL}/api/v1/grants/search"
    
    def __init__(self, db):
        super().__init__(db, "grantconnect.gov.au")
    
    async def scrape(self) -> List[Dict]:
        """
        Scrape grants from GrantConnect.
        Uses their JSON API for better reliability.
        """
        try:
            grants = []
            async with aiohttp.ClientSession() as session:
                # Initial search parameters
                params = {
                    "status": "open",
                    "type": "grant",
                    "page": 1,
                    "limit": 100,
                    "sort": "openDate",
                    "order": "desc"
                }
                
                while True:
                    try:
                        async with session.get(self.SEARCH_URL, params=params) as response:
                            if response.status != 200:
                                logger.error(f"Failed to fetch grants: {response.status}")
                                break
                            
                            data = await response.json()
                            if not data.get("grants"):
                                break
                            
                            for grant in data["grants"]:
                                try:
                                    # Fetch detailed grant info
                                    grant_id = grant["id"]
                                    details = await self._fetch_grant_details(session, grant_id)
                                    
                                    if details:
                                        grant_data = {
                                            "title": grant["title"],
                                            "description": grant["description"],
                                            "source_url": f"{self.BASE_URL}/grants/{grant_id}",
                                            **details
                                        }
                                        grants.append(self.normalize_grant_data(grant_data))
                                
                                except Exception as e:
                                    logger.error(f"Error processing grant {grant.get('title', 'Unknown')}: {str(e)}")
                                    continue
                            
                            # Check if there are more pages
                            if len(data["grants"]) < params["limit"]:
                                break
                            
                            params["page"] += 1
                            
                    except Exception as e:
                        logger.error(f"Error fetching grants page {params['page']}: {str(e)}")
                        break
            
            logger.info(f"Successfully scraped {len(grants)} grants from GrantConnect")
            return grants
            
        except Exception as e:
            logger.error(f"Error scraping GrantConnect: {str(e)}")
            return []
    
    async def _fetch_grant_details(self, session: aiohttp.ClientSession, grant_id: str) -> Dict:
        """
        Fetch detailed grant information using the API.
        """
        try:
            url = f"{self.BASE_URL}/api/v1/grants/{grant_id}"
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch grant details: {response.status}")
                    return {}
                
                data = await response.json()
                grant = data["grant"]
                
                details = {
                    "open_date": grant.get("openDate"),
                    "deadline": grant.get("closeDate"),
                    "min_amount": self._parse_amount(grant.get("estimatedValueFrom")),
                    "max_amount": self._parse_amount(grant.get("estimatedValueTo")),
                    "contact_email": grant.get("contactEmail"),
                    "industry_focus": self._extract_industry(grant.get("categories", [])),
                    "location": self._extract_location(grant.get("eligibility", {})),
                    "org_types": self._extract_org_types(grant.get("eligibility", {})),
                    "funding_purpose": grant.get("fundingPurpose", []),
                    "audience_tags": grant.get("targetGroups", [])
                }
                
                return details
                
        except Exception as e:
            logger.error(f"Error fetching grant details for {grant_id}: {str(e)}")
            return {}
    
    def _parse_amount(self, amount_str: str) -> Optional[int]:
        """Parse amount string to integer."""
        if not amount_str:
            return None
        try:
            return int(float(amount_str))
        except (ValueError, TypeError):
            return None
    
    def _extract_industry(self, categories: List[str]) -> str:
        """Extract industry focus from categories."""
        media_keywords = ["media", "film", "television", "digital", "creative", "arts", "culture"]
        for category in categories:
            if any(keyword in category.lower() for keyword in media_keywords):
                return category
        return "Other"
    
    def _extract_location(self, eligibility: Dict) -> str:
        """Extract location from eligibility criteria."""
        location = eligibility.get("location", "")
        if location.lower() == "all":
            return "National"
        return location
    
    def _extract_org_types(self, eligibility: Dict) -> List[str]:
        """Extract organization types from eligibility criteria."""
        org_types = []
        eligible_types = eligibility.get("organizationTypes", [])
        
        type_mapping = {
            "small_business": ["small business", "sme"],
            "not_for_profit": ["not for profit", "nfp", "non-profit"],
            "social_enterprise": ["social enterprise"],
            "startup": ["startup", "start-up"]
        }
        
        for org_type in eligible_types:
            org_lower = org_type.lower()
            for mapped_type, keywords in type_mapping.items():
                if any(keyword in org_lower for keyword in keywords):
                    org_types.append(mapped_type)
        
        return org_types if org_types else ["any"] 