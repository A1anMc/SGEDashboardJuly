import asyncio
import logging
import random
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from .base_scraper import BaseScraper
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class AustralianGrantsScraper(BaseScraper):
    """
    Comprehensive Australian grants scraper that targets multiple reliable sources
    specifically relevant to media, entertainment, and creative industries.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, "australian_grants")
        self.scraped_grants = []
        self.urls_scraped = []
        self.rate_limits = {"requests_made": 0, "max_per_minute": 30}
        
        # Define target sources with their configurations
        self.sources = {
            "screen_australia": {
                "base_url": "https://www.screenaustralia.gov.au",
                "endpoints": [
                    "/funding-and-support/narrative-content-development",
                    "/funding-and-support/narrative-content-production",
                    "/funding-and-support/documentary",
                    "/funding-and-support/games",
                    "/funding-and-support/online-and-games"
                ],
                "description": "Screen Australia - Government funding for screen content"
            },
            "create_nsw": {
                "base_url": "https://www.create.nsw.gov.au",
                "endpoints": [
                    "/funding-and-support/organisations",
                    "/funding-and-support/individuals",
                    "/funding-and-support/artists-and-creative-practitioners"
                ],
                "description": "Create NSW - NSW state government arts funding"
            },
            "creative_australia": {
                "base_url": "https://creative.gov.au",
                "endpoints": [
                    "/investment-and-development/arts-projects-for-individuals-and-groups",
                    "/investment-and-development/arts-projects-for-organisations",
                    "/investment-and-development/four-year-funding"
                ],
                "description": "Creative Australia - Federal arts funding"
            },
            "business_gov": {
                "base_url": "https://business.gov.au",
                "endpoints": [
                    "/grants-and-programs/creative-industries",
                    "/grants-and-programs/arts-and-culture",
                    "/grants-and-programs/innovation-and-science"
                ],
                "description": "Business.gov.au - Creative industry grants"
            }
        }
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method that coordinates all source scraping."""
        logger.info("Starting Australian grants scraper")
        
        try:
            # Run the async scraping
            self.scraped_grants = await self._scrape_all_sources()
            
            # Filter and validate grants
            valid_grants = []
            for grant in self.scraped_grants:
                if self._validate_grant_data(grant):
                    valid_grants.append(grant)
                else:
                    logger.warning(f"Invalid grant data: {grant.get('title', 'Unknown')}")
            
            logger.info(f"Total valid grants scraped: {len(valid_grants)}")
            return valid_grants
            
        except Exception as e:
            logger.error(f"Error in main scrape method: {str(e)}")
            return []
    
    async def _scrape_all_sources(self) -> List[Dict[str, Any]]:
        """Scrape all sources concurrently with rate limiting."""
        all_grants = []
        
        # Create tasks for each source with delays
        tasks = []
        for i, (source_name, source_config) in enumerate(self.sources.items()):
            # Add progressive delay to avoid overwhelming servers
            delay = i * 2  # 2 seconds between each source start
            task = asyncio.create_task(self._scrape_source_with_delay(source_name, source_config, delay))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            source_name = list(self.sources.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"Error scraping {source_name}: {str(result)}")
            else:
                logger.info(f"Successfully scraped {len(result)} grants from {source_name}")
                all_grants.extend(result)
        
        return all_grants
    
    async def _scrape_source_with_delay(self, source_name: str, source_config: Dict, delay: int) -> List[Dict[str, Any]]:
        """Scrape a source with initial delay."""
        if delay > 0:
            logger.info(f"Waiting {delay} seconds before scraping {source_name}")
            await asyncio.sleep(delay)
        
        return await self._scrape_source(source_name, source_config)
    
    async def _scrape_source(self, source_name: str, source_config: Dict) -> List[Dict[str, Any]]:
        """Scrape a specific source using the BaseScraper _make_request method."""
        grants = []
        base_url = source_config["base_url"]
        
        logger.info(f"Scraping {source_name} from {base_url}")
        
        # Create tasks for each endpoint with delays
        for endpoint in source_config["endpoints"]:
            try:
                url = urljoin(base_url, endpoint)
                
                # Rate limiting
                await self._rate_limit_delay()
                
                # Scrape the endpoint
                endpoint_grants = await self._scrape_endpoint(source_name, url)
                if endpoint_grants:
                    grants.extend(endpoint_grants)
                    logger.info(f"Found {len(endpoint_grants)} grants from {url}")
                
                # Add delay between endpoints
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Error scraping endpoint {endpoint}: {str(e)}")
                continue
        
        return grants
    
    async def _rate_limit_delay(self):
        """Implement rate limiting to be respectful to servers."""
        self.rate_limits["requests_made"] += 1
        
        # Add delay based on request count
        if self.rate_limits["requests_made"] % 10 == 0:
            delay = random.uniform(2, 5)
            logger.info(f"Rate limiting: waiting {delay:.1f} seconds")
            await asyncio.sleep(delay)
    
    async def _scrape_endpoint(self, source_name: str, url: str) -> List[Dict[str, Any]]:
        """Scrape a specific endpoint with retry logic."""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Track URL
                self.urls_scraped.append(url)
                
                # Use BaseScraper's _make_request method
                html = await self._make_request(url)
                if not html:
                    logger.warning(f"Failed to fetch {url} (attempt {attempt + 1})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    return []
                
                soup = self._parse_html(html)
                
                # Use source-specific parsing logic
                grants = []
                if source_name == "screen_australia":
                    grants = await self._parse_screen_australia(soup, url)
                elif source_name == "creative_australia":
                    grants = await self._parse_creative_australia(soup, url)
                elif source_name == "business_gov":
                    grants = await self._parse_business_gov(soup, url)
                elif source_name == "create_nsw":
                    grants = await self._parse_create_nsw(soup, url)
                else:
                    grants = await self._parse_generic(soup, url)
                
                return grants
                
            except Exception as e:
                logger.error(f"Error scraping {url} (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                return []
        
        return []
    
    async def _parse_screen_australia(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse grants from Screen Australia website."""
        grants = []
        
        try:
            # Look for funding opportunity sections
            funding_sections = soup.find_all(['div', 'section'], class_=re.compile(r'funding|grant|opportunity'))
            
            if not funding_sections:
                # Try alternative selectors
                funding_sections = soup.find_all(['div', 'article'], class_=re.compile(r'content|program'))
            
            # If still no sections, extract from main content
            if not funding_sections:
                main_content = soup.find('main') or soup.find('div', class_='content')
                if main_content:
                    funding_sections = [main_content]
            
            for section in funding_sections:
                grant_info = await self._extract_grant_info(section, url, "screen_australia")
                if grant_info:
                    grants.append(grant_info)
            
            # Also check for the main page grant info
            main_grant = await self._extract_main_grant_info(soup, url, "screen_australia")
            if main_grant and main_grant not in grants:
                grants.append(main_grant)
                
        except Exception as e:
            logger.error(f"Error parsing Screen Australia page {url}: {str(e)}")
        
        return grants
    
    async def _parse_creative_australia(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse grants from Creative Australia website."""
        grants = []
        
        try:
            # Look for grant/funding sections
            grant_sections = soup.find_all(['div', 'section'], class_=re.compile(r'grant|funding|program'))
            
            if not grant_sections:
                # Try content sections
                grant_sections = soup.find_all(['div', 'article'], class_=re.compile(r'content|main'))
            
            for section in grant_sections:
                grant_info = await self._extract_grant_info(section, url, "creative_australia")
                if grant_info:
                    grants.append(grant_info)
            
            # Extract main page info
            main_grant = await self._extract_main_grant_info(soup, url, "creative_australia")
            if main_grant:
                grants.append(main_grant)
                
        except Exception as e:
            logger.error(f"Error parsing Creative Australia page {url}: {str(e)}")
        
        return grants
    
    async def _parse_business_gov(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse grants from Business.gov.au website."""
        grants = []
        
        try:
            # Look for grant cards or listings
            grant_cards = soup.find_all(['div', 'article'], class_=re.compile(r'card|grant|program|listing'))
            
            for card in grant_cards:
                grant_info = await self._extract_grant_info(card, url, "business_gov")
                if grant_info:
                    grants.append(grant_info)
            
            # Extract main page info if no cards found
            if not grants:
                main_grant = await self._extract_main_grant_info(soup, url, "business_gov")
                if main_grant:
                    grants.append(main_grant)
                    
        except Exception as e:
            logger.error(f"Error parsing Business.gov.au page {url}: {str(e)}")
        
        return grants
    
    async def _parse_create_nsw(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse grants from Create NSW website."""
        grants = []
        
        try:
            # Look for funding opportunity sections
            funding_sections = soup.find_all(['div', 'section'], class_=re.compile(r'funding|grant|opportunity'))
            
            for section in funding_sections:
                grant_info = await self._extract_grant_info(section, url, "create_nsw")
                if grant_info:
                    grants.append(grant_info)
            
            # Extract main page info
            main_grant = await self._extract_main_grant_info(soup, url, "create_nsw")
            if main_grant:
                grants.append(main_grant)
                
        except Exception as e:
            logger.error(f"Error parsing Create NSW page {url}: {str(e)}")
        
        return grants
    
    async def _parse_generic(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Generic parser for unknown sources."""
        grants = []
        
        try:
            # Extract main page info
            main_grant = await self._extract_main_grant_info(soup, url, "generic")
            if main_grant:
                grants.append(main_grant)
                
        except Exception as e:
            logger.error(f"Error parsing generic page {url}: {str(e)}")
        
        return grants
    
    async def _extract_grant_info(self, element: BeautifulSoup, source_url: str, source_name: str) -> Optional[Dict[str, Any]]:
        """Extract grant information from a page element."""
        try:
            # Look for title
            title_element = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            title = title_element.get_text(strip=True) if title_element else ""
            
            # Skip if no meaningful title
            if not title or len(title) < 10:
                return None
            
            # Look for description
            description = self._extract_description(element)
            if not description:
                return None
            
            # Extract other information
            element_text = element.get_text()
            min_amount, max_amount = self._extract_amounts(element_text)
            dates = self._extract_dates(element_text)
            contact_email = self._extract_email(element_text)
            
            # Create properly normalized grant data
            grant_data = {
                "title": title,
                "description": description,
                "source_url": source_url,
                "min_amount": min_amount,
                "max_amount": max_amount,
                "open_date": dates.get("open_date"),
                "deadline": dates.get("deadline"),
                "contact_email": contact_email or "",
                "industry_focus": self._determine_industry_focus(title + " " + description),
                "location": "national",
                "org_types": self._extract_org_types(element_text),
                "funding_purpose": self._extract_funding_purpose(title + " " + description),
                "audience_tags": self._extract_audience_tags(title + " " + description),
                "status": "active"
            }
            
            # Use BaseScraper's normalize_grant_data method
            return self.normalize_grant_data(grant_data)
            
        except Exception as e:
            logger.error(f"Error extracting grant info: {str(e)}")
            return None
    
    async def _extract_main_grant_info(self, soup: BeautifulSoup, url: str, source_name: str) -> Optional[Dict[str, Any]]:
        """Extract main grant information from the primary content of a page."""
        try:
            # Get the main title
            title_element = soup.find('h1')
            if not title_element:
                # Try alternative title selectors
                title_element = soup.find(['h2', 'h3'], class_=re.compile(r'title|heading'))
            
            if not title_element:
                return None
                
            title = title_element.get_text(strip=True)
            
            # Skip if title is too short or generic
            if len(title) < 10 or any(word in title.lower() for word in ['home', 'welcome', 'about', 'contact']):
                return None
            
            # Get the main description from the page
            description = self._extract_page_description(soup)
            if not description:
                return None
            
            # Extract other information from the full page
            page_text = soup.get_text()
            min_amount, max_amount = self._extract_amounts(page_text)
            dates = self._extract_dates(page_text)
            contact_email = self._extract_email(page_text)
            
            # Create properly normalized grant data
            grant_data = {
                "title": title,
                "description": description,
                "source_url": url,
                "min_amount": min_amount,
                "max_amount": max_amount,
                "open_date": dates.get("open_date"),
                "deadline": dates.get("deadline"),
                "contact_email": contact_email or "",
                "industry_focus": self._determine_industry_focus(title + " " + description),
                "location": "national",
                "org_types": self._extract_org_types(page_text),
                "funding_purpose": self._extract_funding_purpose(title + " " + description),
                "audience_tags": self._extract_audience_tags(title + " " + description),
                "status": "active"
            }
            
            # Use BaseScraper's normalize_grant_data method
            return self.normalize_grant_data(grant_data)
            
        except Exception as e:
            logger.error(f"Error extracting main grant info from {url}: {str(e)}")
            return None
    
    def _extract_description(self, element: BeautifulSoup) -> Optional[str]:
        """Extract description from an element."""
        # Look for description in various ways
        desc_selectors = [
            'p',
            'div.description',
            'div.summary',
            'div.content',
            '.excerpt'
        ]
        
        for selector in desc_selectors:
            desc_elem = element.find(selector)
            if desc_elem:
                text = desc_elem.get_text(strip=True)
                if len(text) > 50:  # Ensure meaningful description
                    return text[:500]  # Limit length
        
        return None
    
    def _extract_page_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract description from the main page content."""
        # Look for main content areas
        content_selectors = [
            'main',
            '.main-content',
            '.content',
            '.page-content',
            'article'
        ]
        
        for selector in content_selectors:
            content_elem = soup.find(selector)
            if content_elem:
                # Get first few paragraphs
                paragraphs = content_elem.find_all('p')[:3]
                if paragraphs:
                    text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    if len(text) > 100:
                        return text[:1000]  # Limit length
        
        return None
    
    def _extract_amounts(self, text: str) -> tuple:
        """Extract funding amounts from text."""
        min_amount = None
        max_amount = None
        
        # Look for dollar amounts
        amount_patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)',
            r'([0-9,]+(?:\.[0-9]{2})?) dollars?',
            r'up to \$([0-9,]+)',
            r'maximum \$([0-9,]+)',
            r'minimum \$([0-9,]+)'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = int(match.replace(',', ''))
                    if 'up to' in text.lower() or 'maximum' in text.lower():
                        max_amount = amount
                    elif 'minimum' in text.lower():
                        min_amount = amount
                    else:
                        # If no qualifier, assume it's the maximum
                        max_amount = amount
                except ValueError:
                    continue
        
        return min_amount, max_amount
    
    def _extract_dates(self, text: str) -> Dict[str, Optional[str]]:
        """Extract dates from text."""
        dates = {"open_date": None, "deadline": None}
        
        # Look for date patterns
        date_patterns = [
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
            r'(\d{1,2} [A-Za-z]+ \d{4})',
            r'([A-Za-z]+ \d{1,2}, \d{4})',
            r'(\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Try to determine if it's an open date or deadline
                context = text[max(0, text.find(match) - 50):text.find(match) + 50].lower()
                if any(word in context for word in ['open', 'start', 'begin']):
                    dates["open_date"] = match
                elif any(word in context for word in ['close', 'deadline', 'due', 'end']):
                    dates["deadline"] = match
        
        return dates
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None
    
    def _determine_industry_focus(self, text: str) -> str:
        """Determine industry focus from text."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['screen', 'film', 'television', 'tv', 'movie', 'cinema']):
            return "screen"
        elif any(word in text_lower for word in ['game', 'gaming', 'interactive', 'digital']):
            return "games"
        elif any(word in text_lower for word in ['art', 'creative', 'culture', 'music', 'theatre']):
            return "arts"
        elif any(word in text_lower for word in ['media', 'content', 'production']):
            return "media"
        else:
            return "creative"
    
    def _extract_org_types(self, text: str) -> List[str]:
        """Extract organization types from text."""
        text_lower = text.lower()
        org_types = []
        
        if any(word in text_lower for word in ['individual', 'artist', 'freelancer']):
            org_types.append("individual")
        if any(word in text_lower for word in ['small business', 'sme', 'startup']):
            org_types.append("small_business")
        if any(word in text_lower for word in ['non-profit', 'not-for-profit', 'charity']):
            org_types.append("not_for_profit")
        if any(word in text_lower for word in ['company', 'corporation', 'enterprise']):
            org_types.append("company")
        
        return org_types if org_types else ["any"]
    
    def _extract_funding_purpose(self, text: str) -> List[str]:
        """Extract funding purpose from text."""
        text_lower = text.lower()
        purposes = []
        
        if any(word in text_lower for word in ['development', 'develop', 'create']):
            purposes.append("development")
        if any(word in text_lower for word in ['production', 'produce', 'make']):
            purposes.append("production")
        if any(word in text_lower for word in ['research', 'study', 'investigate']):
            purposes.append("research")
        if any(word in text_lower for word in ['marketing', 'promotion', 'distribute']):
            purposes.append("marketing")
        
        return purposes if purposes else ["development"]
    
    def _extract_audience_tags(self, text: str) -> List[str]:
        """Extract audience tags from text."""
        text_lower = text.lower()
        tags = []
        
        if any(word in text_lower for word in ['emerging', 'new', 'early career']):
            tags.append("emerging")
        if any(word in text_lower for word in ['established', 'experienced', 'professional']):
            tags.append("established")
        if any(word in text_lower for word in ['indigenous', 'aboriginal', 'first nations']):
            tags.append("indigenous")
        if any(word in text_lower for word in ['diverse', 'multicultural', 'inclusive']):
            tags.append("diverse")
        
        return tags if tags else ["general"]
    
    def _validate_grant_data(self, data: Dict[str, Any]) -> bool:
        """Enhanced validation for grant data."""
        if not super()._validate_grant_data(data):
            return False
        
        # Additional validation
        title = data.get("title", "")
        description = data.get("description", "")
        
        # Skip if title or description is too short
        if len(title) < 10 or len(description) < 50:
            return False
        
        # Skip if title contains generic terms
        generic_terms = ['home', 'welcome', 'about', 'contact', 'privacy', 'terms']
        if any(term in title.lower() for term in generic_terms):
            return False
        
        return True