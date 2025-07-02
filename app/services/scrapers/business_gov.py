import aiohttp
import logging
from bs4 import BeautifulSoup
from typing import List, Dict
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

class BusinessGovScraper(BaseScraper):
    """Scraper for business.gov.au grants."""
    
    BASE_URL = "https://business.gov.au"
    GRANTS_URL = f"{BASE_URL}/grants-and-programs"
    
    def __init__(self, db):
        super().__init__(db, "business.gov.au")
    
    async def scrape(self) -> List[Dict]:
        """
        Scrape grants from business.gov.au.
        Returns list of normalized grant dictionaries.
        """
        try:
            grants = []
            async with aiohttp.ClientSession() as session:
                # Fetch main grants page
                async with session.get(self.GRANTS_URL) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch grants page: {response.status}")
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Find all grant cards/listings
                    grant_elements = soup.find_all('div', class_='grant-card')
                    
                    for element in grant_elements:
                        try:
                            # Extract basic info
                            title = element.find('h3').text.strip()
                            description = element.find('div', class_='description').text.strip()
                            link = element.find('a')['href']
                            
                            # Fetch detailed grant page
                            full_url = f"{self.BASE_URL}{link}" if link.startswith('/') else link
                            grant_details = await self._fetch_grant_details(session, full_url)
                            
                            if grant_details:
                                grant_data = {
                                    "title": title,
                                    "description": description,
                                    "source_url": full_url,
                                    **grant_details
                                }
                                grants.append(self.normalize_grant_data(grant_data))
                            
                        except Exception as e:
                            logger.error(f"Error processing grant {title if 'title' in locals() else 'Unknown'}: {str(e)}")
                            continue
            
            logger.info(f"Successfully scraped {len(grants)} grants from business.gov.au")
            return grants
            
        except Exception as e:
            logger.error(f"Error scraping business.gov.au: {str(e)}")
            return []
    
    async def _fetch_grant_details(self, session: aiohttp.ClientSession, url: str) -> Dict:
        """
        Fetch and parse detailed grant information.
        """
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch grant details: {response.status}")
                    return {}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                details = {}
                
                # Extract dates
                date_elements = soup.find_all('div', class_='date-field')
                for date_elem in date_elements:
                    label = date_elem.find('label').text.lower()
                    if 'open' in label:
                        details['open_date'] = date_elem.find('span').text.strip()
                    elif 'close' in label or 'deadline' in label:
                        details['deadline'] = date_elem.find('span').text.strip()
                
                # Extract funding amounts
                amount_elem = soup.find('div', class_='funding-amount')
                if amount_elem:
                    amount_text = amount_elem.text
                    if 'up to' in amount_text.lower():
                        details['max_amount'] = self._extract_amount(amount_text)
                    elif 'minimum' in amount_text.lower():
                        details['min_amount'] = self._extract_amount(amount_text)
                
                # Extract eligibility
                eligibility_elem = soup.find('div', class_='eligibility')
                if eligibility_elem:
                    org_types = []
                    for item in eligibility_elem.find_all('li'):
                        text = item.text.lower()
                        if any(term in text for term in ['business', 'organisation', 'enterprise']):
                            org_types.append(text)
                    details['org_types'] = org_types
                
                # Extract industry focus
                industry_elem = soup.find('div', class_='industry-sectors')
                if industry_elem:
                    details['industry_focus'] = industry_elem.text.strip()
                
                # Extract location
                location_elem = soup.find('div', class_='location')
                if location_elem:
                    details['location'] = location_elem.text.strip()
                
                # Extract contact info
                contact_elem = soup.find('div', class_='contact-info')
                if contact_elem:
                    email = contact_elem.find('a', href=lambda x: x and 'mailto:' in x)
                    if email:
                        details['contact_email'] = email['href'].replace('mailto:', '')
                
                return details
                
        except Exception as e:
            logger.error(f"Error fetching grant details from {url}: {str(e)}")
            return {}
    
    def _extract_amount(self, text: str) -> int:
        """Extract numeric amount from text."""
        try:
            # Remove currency symbols and commas, then extract numbers
            cleaned = text.replace('$', '').replace(',', '')
            import re
            numbers = re.findall(r'\d+', cleaned)
            if numbers:
                return int(numbers[0])
        except Exception:
            pass
        return None 