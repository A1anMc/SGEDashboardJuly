import aiohttp
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from .base_scraper import BaseScraper
import asyncio
import random
import re

logger = logging.getLogger(__name__)

class CustomScraper(BaseScraper):
    """Custom scraper that uses web scraping instead of APIs."""
    
    def __init__(self, db):
        super().__init__(db, "custom_source")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
    async def scrape(self) -> List[Dict]:
        """Scrape grants using web scraping."""
        grants = []
        try:
            # Define target URLs
            urls = [
                "https://www.arts.gov.au/funding-and-support",
                "https://www.screenaustralia.gov.au/funding-and-support",
                # Add more URLs as needed
            ]
            
            async with aiohttp.ClientSession(headers=self.headers) as session:
                for url in urls:
                    try:
                        # Add random delay between requests to be polite
                        await asyncio.sleep(random.uniform(1, 3))
                        
                        async with session.get(url) as response:
                            if response.status != 200:
                                logger.error(f"Failed to fetch {url}: {response.status}")
                                continue
                                
                            html = await response.text()
                            soup = BeautifulSoup(html, "html.parser")
                            
                            # Extract grants based on URL
                            if "arts.gov.au" in url:
                                grants.extend(await self._parse_arts_gov(soup, url))
                            elif "screenaustralia.gov.au" in url:
                                grants.extend(await self._parse_screen_australia(soup, url))
                            
                    except Exception as e:
                        logger.error(f"Error scraping {url}: {str(e)}")
                        continue
                        
            return grants
            
        except Exception as e:
            logger.error(f"Error in scraper: {str(e)}")
            return []
            
    async def _parse_arts_gov(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse grants from arts.gov.au."""
        grants = []
        try:
            # Find grant listings
            grant_elements = soup.find_all("div", class_="grant-listing")
            
            for element in grant_elements:
                try:
                    title = element.find("h3").text.strip()
                    description = element.find("div", class_="description").text.strip()
                    link = element.find("a")["href"]
                    full_url = f"{base_url}{link}" if link.startswith("/") else link
                    
                    # Get grant details
                    details = await self._fetch_grant_details(full_url)
                    
                    if details:
                        grant_data = {
                            "title": title,
                            "description": description,
                            "source_url": full_url,
                            **details
                        }
                        grants.append(self.normalize_grant_data(grant_data))
                        
                except Exception as e:
                    logger.error(f"Error parsing grant {title if 'title' in locals() else 'Unknown'}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing arts.gov.au: {str(e)}")
            
        return grants
        
    async def _parse_screen_australia(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Parse grants from screenaustralia.gov.au."""
        grants = []
        try:
            # Find grant listings
            grant_elements = soup.find_all("div", class_="funding-opportunity")
            
            for element in grant_elements:
                try:
                    title = element.find("h2").text.strip()
                    description = element.find("div", class_="summary").text.strip()
                    link = element.find("a")["href"]
                    full_url = f"{base_url}{link}" if link.startswith("/") else link
                    
                    # Get grant details
                    details = await self._fetch_grant_details(full_url)
                    
                    if details:
                        grant_data = {
                            "title": title,
                            "description": description,
                            "source_url": full_url,
                            **details
                        }
                        grants.append(self.normalize_grant_data(grant_data))
                        
                except Exception as e:
                    logger.error(f"Error parsing grant {title if 'title' in locals() else 'Unknown'}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing screenaustralia.gov.au: {str(e)}")
            
        return grants
        
    async def _fetch_grant_details(self, url: str) -> Optional[Dict]:
        """Fetch and parse detailed grant information."""
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch grant details: {response.status}")
                        return None
                        
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    
                    details = {}
                    
                    # Extract dates
                    dates = soup.find_all("div", class_="date")
                    for date_elem in dates:
                        label = date_elem.find("label").text.lower()
                        if "open" in label:
                            details["open_date"] = date_elem.find("span").text.strip()
                        elif "close" in label:
                            details["deadline"] = date_elem.find("span").text.strip()
                            
                    # Extract funding amount
                    amount_elem = soup.find("div", class_="funding-amount")
                    if amount_elem:
                        amount_text = amount_elem.text.lower()
                        if "up to" in amount_text:
                            details["max_amount"] = self._extract_amount(amount_text)
                        elif "minimum" in amount_text:
                            details["min_amount"] = self._extract_amount(amount_text)
                            
                    # Extract contact info
                    contact = soup.find("div", class_="contact-info")
                    if contact:
                        email = contact.find("a", href=lambda x: x and "mailto:" in x)
                        if email:
                            details["contact_email"] = email["href"].replace("mailto:", "")
                            
                    # Extract industry focus
                    industry = soup.find("div", class_="industry")
                    if industry:
                        details["industry_focus"] = industry.text.strip()
                        
                    # Extract location
                    location = soup.find("div", class_="location")
                    if location:
                        details["location"] = location.text.strip()
                        
                    return details
                    
        except Exception as e:
            logger.error(f"Error fetching grant details from {url}: {str(e)}")
            return None
            
    def _extract_amount(self, text: str) -> Optional[int]:
        """Extract numeric amount from text."""
        try:
            # Remove currency symbols and commas
            cleaned = text.replace("$", "").replace(",", "")
            numbers = re.findall(r"\d+", cleaned)
            if numbers:
                return int(numbers[0])
        except Exception:
            pass
        return None 