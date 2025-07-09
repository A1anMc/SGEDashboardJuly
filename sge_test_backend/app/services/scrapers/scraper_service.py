import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.grant import Grant
import aiohttp
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, db: Session):
        self.db = db

    async def scrape(self) -> List[dict]:
        """
        Implement this method in each scraper to return a list of grant dictionaries.
        """
        raise NotImplementedError

    def save_grants(self, grants: List[dict]) -> None:
        """
        Save scraped grants to the database.
        """
        for grant_data in grants:
            existing = self.db.query(Grant).filter(
                Grant.source == grant_data["source"],
                Grant.source_url == grant_data["source_url"]
            ).first()

            if existing:
                # Update existing grant
                for key, value in grant_data.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                # Create new grant
                grant = Grant(**grant_data)
                self.db.add(grant)

        self.db.commit()

class BusinessGovScraper(BaseScraper):
    async def scrape(self) -> List[dict]:
        """Scrape grants from Business.gov.au."""
        logger.info("Running Business.gov.au scraper")
        grants = []
        
        async with aiohttp.ClientSession() as session:
            try:
                # Fetch main grants page
                async with session.get("https://business.gov.au/grants-and-programs") as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch grants list: {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    grant_cards = soup.find_all('div', class_='grant-card')
                    
                    for card in grant_cards:
                        try:
                            title = card.find('h3').text.strip()
                            description = card.find('div', class_='description').text.strip()
                            link = card.find('a')['href']
                            
                            # Fetch detailed grant information
                            details = await self._fetch_grant_details(session, link)
                            if not details:
                                continue
                            
                            grant_data = {
                                "title": title,
                                "description": description,
                                "source": "business.gov.au",
                                "source_url": f"https://business.gov.au{link}",
                                "open_date": details.get("open_date"),
                                "deadline": details.get("deadline"),
                                "max_amount": details.get("max_amount"),
                                "min_amount": None,  # Not provided by business.gov.au
                                "industry_focus": self._normalize_industry(details.get("industry_focus")),
                                "location_eligibility": self._normalize_location(details.get("location")),
                                "org_type_eligible": self._normalize_org_types(details.get("org_types", [])),
                                "contact_email": details.get("contact_email"),
                                "status": "open"  # Default to open since we're scraping active grants
                            }
                            grants.append(grant_data)
                            
                        except Exception as e:
                            logger.error(f"Error processing grant card: {str(e)}")
                            continue
                            
            except Exception as e:
                logger.error(f"Error scraping Business.gov.au: {str(e)}")
                return []
                
        return grants
        
    async def _fetch_grant_details(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Fetch detailed information for a specific grant."""
        try:
            async with session.get(f"https://business.gov.au{url}") as response:
                if response.status != 200:
                    return {}
                    
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                details = {}
                
                # Extract dates
                date_fields = soup.find_all('div', class_='date-field')
                for field in date_fields:
                    label = field.find('label').text.lower()
                    date = field.find('span').text
                    if 'opening' in label:
                        details['open_date'] = date
                    elif 'closing' in label:
                        details['deadline'] = date
                
                # Extract funding amount
                funding_div = soup.find('div', class_='funding-amount')
                if funding_div:
                    details['max_amount'] = self._extract_amount(funding_div.text)
                
                # Extract eligibility
                eligibility_div = soup.find('div', class_='eligibility')
                if eligibility_div:
                    org_types = [li.text.strip() for li in eligibility_div.find_all('li')]
                    details['org_types'] = org_types
                
                # Extract industry focus
                industry_div = soup.find('div', class_='industry-sectors')
                if industry_div:
                    details['industry_focus'] = industry_div.text.strip()
                
                # Extract location
                location_div = soup.find('div', class_='location')
                if location_div:
                    details['location'] = location_div.text.strip()
                
                # Extract contact email
                contact_div = soup.find('div', class_='contact-info')
                if contact_div:
                    email_link = contact_div.find('a', href=lambda x: x and 'mailto:' in x)
                    if email_link:
                        details['contact_email'] = email_link['href'].replace('mailto:', '')
                
                return details
                
        except Exception as e:
            logger.error(f"Error fetching grant details: {str(e)}")
            return {}
            
    def _extract_amount(self, amount_str: str) -> Optional[int]:
        """Extract numeric amount from string."""
        try:
            # Remove currency symbol and commas, then find the first number
            cleaned = amount_str.replace('$', '').replace(',', '')
            match = re.search(r'\d+', cleaned)
            if match:
                return int(match.group())
            return None
        except Exception:
            return None

class GrantConnectScraper(BaseScraper):
    async def scrape(self) -> List[dict]:
        """Scrape grants from GrantConnect API."""
        logger.info("Running GrantConnect scraper")
        grants = []
        
        async with aiohttp.ClientSession() as session:
            try:
                # Fetch grants list from API
                async with session.get("https://www.grants.gov.au/api/v1/grants/search") as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch grants list: {response.status}")
                        return []
                    
                    data = await response.json()
                    for grant_summary in data.get("grants", []):
                        try:
                            grant_id = grant_summary["id"]
                            
                            # Fetch detailed grant information
                            details = await self._fetch_grant_details(session, grant_id)
                            if not details:
                                continue
                            
                            grant_data = {
                                "title": grant_summary["title"],
                                "description": grant_summary["description"],
                                "source": "grantconnect.gov.au",
                                "source_url": f"https://www.grants.gov.au/grants/{grant_id}",
                                "open_date": details.get("open_date"),
                                "deadline": details.get("deadline"),
                                "max_amount": details.get("max_amount"),
                                "min_amount": details.get("min_amount"),
                                "industry_focus": self._normalize_industry(details.get("industry_focus")),
                                "location_eligibility": self._normalize_location(details.get("location")),
                                "org_type_eligible": self._normalize_org_types(details.get("org_types", [])),
                                "contact_email": details.get("contact_email"),
                                "status": "open"  # Default to open since we're scraping active grants
                            }
                            grants.append(grant_data)
                            
                        except Exception as e:
                            logger.error(f"Error processing grant {grant_id}: {str(e)}")
                            continue
                            
            except Exception as e:
                logger.error(f"Error scraping GrantConnect: {str(e)}")
                return []
                
        return grants
        
    async def _fetch_grant_details(self, session: aiohttp.ClientSession, grant_id: str) -> Dict[str, Any]:
        """Fetch detailed information for a specific grant."""
        try:
            async with session.get(f"https://www.grants.gov.au/api/v1/grants/{grant_id}") as response:
                if response.status != 200:
                    return {}
                    
                data = await response.json()
                details = {
                    "open_date": data.get("open_date"),
                    "deadline": data.get("deadline"),
                    "min_amount": data.get("min_amount"),
                    "max_amount": data.get("max_amount"),
                    "contact_email": data.get("contact_email"),
                    "industry_focus": data.get("industry_focus"),
                    "location": data.get("location"),
                    "org_types": data.get("org_types", []),
                    "funding_purpose": data.get("funding_purpose", []),
                    "audience_tags": data.get("audience_tags", [])
                }
                return details
                
        except Exception as e:
            logger.error(f"Error fetching grant details: {str(e)}")
            return {}

class CommunityGrantsScraper(BaseScraper):
    async def scrape(self) -> List[dict]:
        """Scrape grants from Community Grants sources."""
        logger.info("Running Community Grants scraper")
        
        try:
            # TODO: Add specific community grant sources
            # For now, return an empty list as this scraper is not yet fully implemented
            logger.info("Community Grants scraper is not yet implemented")
            return []
            
        except Exception as e:
            logger.error(f"Error scraping Community Grants: {str(e)}")
            return []

async def run_all_scrapers(db: Session) -> None:
    """
    Run all grant scrapers and save results to the database.
    """
    scrapers = [
        BusinessGovScraper(db),
        GrantConnectScraper(db),
        CommunityGrantsScraper(db)
    ]

    for scraper in scrapers:
        try:
            grants = await scraper.scrape()
            scraper.save_grants(grants)
            logger.info(f"Successfully ran {scraper.__class__.__name__}")
        except Exception as e:
            logger.error(f"Error running {scraper.__class__.__name__}: {str(e)}")
            continue 