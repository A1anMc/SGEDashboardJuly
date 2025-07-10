import aiohttp
import asyncio
import logging
import random
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse
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
        self.session = None
        self.scraped_grants = []
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        # Define target sources with their configurations
        self.sources = {
            "screen_australia": {
                "base_url": "https://www.screenaustralia.gov.au",
                "endpoints": [
                    "/funding-and-support/narrative-content-development",
                    "/funding-and-support/narrative-content-production",
                    "/funding-and-support/documentary",
                    "/funding-and-support/games",
                    "/funding-and-support/industry-development"
                ],
                "description": "Screen Australia - Government funding for screen content"
            },
            "creative_australia": {
                "base_url": "https://creative.gov.au",
                "endpoints": [
                    "/investment-and-development/arts-projects-for-individuals-and-groups",
                    "/investment-and-development/arts-projects-for-organisations",
                    "/investment-and-development/multi-year-investment"
                ],
                "description": "Creative Australia - Federal arts funding"
            },
            "business_gov": {
                "base_url": "https://business.gov.au",
                "endpoints": [
                    "/grants-and-programs/screen-australia-funding-and-support",
                    "/grants-and-programs/arts-and-culture",
                    "/grants-and-programs/creative-industries"
                ],
                "description": "Business.gov.au - Creative industry grants"
            },
            "create_nsw": {
                "base_url": "https://www.create.nsw.gov.au",
                "endpoints": [
                    "/funding-and-support/organisations",
                    "/funding-and-support/individuals",
                    "/funding-and-support/quick-response"
                ],
                "description": "Create NSW - NSW state government arts funding"
            }
        }
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method that coordinates all source scraping."""
        logger.info("Starting Australian grants scraper")
        
        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            self.session = session
            
            # Scrape each source
            for source_name, source_config in self.sources.items():
                try:
                    logger.info(f"Scraping {source_name}")
                    grants = await self._scrape_source(source_name, source_config)
                    self.scraped_grants.extend(grants)
                    logger.info(f"Found {len(grants)} grants from {source_name}")
                    
                    # Be respectful - add delay between sources
                    await asyncio.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"Error scraping {source_name}: {str(e)}")
                    continue
        
        logger.info(f"Total grants scraped: {len(self.scraped_grants)}")
        return self.scraped_grants
    
    async def _scrape_source(self, source_name: str, source_config: Dict) -> List[Dict[str, Any]]:
        """Scrape a specific source."""
        grants = []
        base_url = source_config["base_url"]
        
        for endpoint in source_config["endpoints"]:
            try:
                url = urljoin(base_url, endpoint)
                
                # Add random delay between requests
                await asyncio.sleep(random.uniform(1, 2))
                
                async with self.session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch {url}: {response.status}")
                        continue
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Use source-specific parsing logic
                    if source_name == "screen_australia":
                        page_grants = await self._parse_screen_australia(soup, url)
                    elif source_name == "creative_australia":
                        page_grants = await self._parse_creative_australia(soup, url)
                    elif source_name == "business_gov":
                        page_grants = await self._parse_business_gov(soup, url)
                    elif source_name == "create_nsw":
                        page_grants = await self._parse_create_nsw(soup, url)
                    else:
                        page_grants = await self._parse_generic(soup, url)
                    
                    grants.extend(page_grants)
                    
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                continue
        
        return grants
    
    async def _parse_screen_australia(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse grants from Screen Australia pages."""
        grants = []
        
        try:
            # Look for funding program information
            funding_sections = soup.find_all(['div', 'section'], class_=re.compile(r'funding|grant|program'))
            
            for section in funding_sections:
                grant_info = await self._extract_grant_info(section, url, "Screen Australia")
                if grant_info:
                    grants.append(grant_info)
            
            # Also look for structured content
            content_blocks = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'content|main|body'))
            for block in content_blocks:
                grant_info = await self._extract_grant_info(block, url, "Screen Australia")
                if grant_info:
                    grants.append(grant_info)
                    
        except Exception as e:
            logger.error(f"Error parsing Screen Australia page {url}: {str(e)}")
        
        return grants
    
    async def _parse_creative_australia(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse grants from Creative Australia pages."""
        grants = []
        
        try:
            # Look for grant listings and details
            grant_elements = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'grant|funding|opportunity'))
            
            for element in grant_elements:
                grant_info = await self._extract_grant_info(element, url, "Creative Australia")
                if grant_info:
                    grants.append(grant_info)
            
            # Check for specific patterns in Creative Australia pages
            title_element = soup.find('h1')
            if title_element:
                main_grant = await self._extract_main_grant_info(soup, url, "Creative Australia")
                if main_grant:
                    grants.append(main_grant)
                    
        except Exception as e:
            logger.error(f"Error parsing Creative Australia page {url}: {str(e)}")
        
        return grants
    
    async def _parse_business_gov(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse grants from Business.gov.au pages."""
        grants = []
        
        try:
            # Look for grant program information
            program_sections = soup.find_all(['div', 'section'], class_=re.compile(r'program|grant|funding'))
            
            for section in program_sections:
                grant_info = await self._extract_grant_info(section, url, "Business.gov.au")
                if grant_info:
                    grants.append(grant_info)
            
            # Check for the main content
            main_content = soup.find('main') or soup.find('div', class_=re.compile(r'main|content'))
            if main_content:
                grant_info = await self._extract_main_grant_info(main_content, url, "Business.gov.au")
                if grant_info:
                    grants.append(grant_info)
                    
        except Exception as e:
            logger.error(f"Error parsing Business.gov.au page {url}: {str(e)}")
        
        return grants
    
    async def _parse_create_nsw(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse grants from Create NSW pages."""
        grants = []
        
        try:
            # Look for NSW-specific funding information
            funding_sections = soup.find_all(['div', 'section'], class_=re.compile(r'funding|grant|program'))
            
            for section in funding_sections:
                grant_info = await self._extract_grant_info(section, url, "Create NSW")
                if grant_info:
                    grants.append(grant_info)
                    
        except Exception as e:
            logger.error(f"Error parsing Create NSW page {url}: {str(e)}")
        
        return grants
    
    async def _parse_generic(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Generic parser for unknown sources."""
        grants = []
        
        try:
            # Look for common grant-related patterns
            elements = soup.find_all(['div', 'article', 'section'], 
                                   class_=re.compile(r'grant|funding|opportunity|program', re.I))
            
            for element in elements:
                grant_info = await self._extract_grant_info(element, url, "Australian Government")
                if grant_info:
                    grants.append(grant_info)
                    
        except Exception as e:
            logger.error(f"Error parsing page {url}: {str(e)}")
        
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
            description_elements = element.find_all(['p', 'div'], class_=re.compile(r'description|summary|overview'))
            description = ""
            for desc_elem in description_elements:
                desc_text = desc_elem.get_text(strip=True)
                if desc_text and len(desc_text) > 20:
                    description = desc_text[:500] + "..." if len(desc_text) > 500 else desc_text
                    break
            
            if not description:
                # Fallback to getting text from paragraphs
                paragraphs = element.find_all('p')
                for p in paragraphs[:3]:  # Check first 3 paragraphs
                    text = p.get_text(strip=True)
                    if text and len(text) > 20:
                        description = text[:500] + "..." if len(text) > 500 else text
                        break
            
            # Look for amount information
            amount_text = element.get_text()
            min_amount, max_amount = self._extract_amounts(amount_text)
            
            # Look for dates
            dates = self._extract_dates(element.get_text())
            
            # Look for contact info
            contact_email = self._extract_email(element.get_text())
            
            # Generate a unique identifier for this grant
            grant_id = f"{source_name}_{abs(hash(title + source_url))}"
            
            grant_info = {
                "title": title,
                "description": description,
                "source": source_name,
                "source_url": source_url,
                "amount_min": min_amount,
                "amount_max": max_amount,
                "open_date": dates.get("open_date"),
                "deadline": dates.get("deadline"),
                "contact_email": contact_email,
                "industry_focus": self._determine_industry_focus(title + " " + description),
                "location": "Australia",
                "eligibility_criteria": self._extract_eligibility(element.get_text()),
                "org_type": self._extract_org_types(element.get_text()),
                "status": "open",  # Default to open, can be refined
                "scraped_at": datetime.now().isoformat(),
                "grant_id": grant_id
            }
            
            return grant_info
            
        except Exception as e:
            logger.error(f"Error extracting grant info: {str(e)}")
            return None
    
    async def _extract_main_grant_info(self, soup: BeautifulSoup, url: str, source_name: str) -> Optional[Dict[str, Any]]:
        """Extract main grant information from the primary content of a page."""
        try:
            # Get the main title
            title_element = soup.find('h1')
            if not title_element:
                return None
                
            title = title_element.get_text(strip=True)
            
            # Get the main description from the page
            description = ""
            
            # Look for meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                description = meta_desc.get('content', '')
            
            # If no meta description, get from main content
            if not description:
                content_selectors = [
                    'div[class*="content"]',
                    'main',
                    'article',
                    'section[class*="main"]'
                ]
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        paragraphs = content_elem.find_all('p')
                        for p in paragraphs[:3]:
                            text = p.get_text(strip=True)
                            if text and len(text) > 50:
                                description = text[:500] + "..." if len(text) > 500 else text
                                break
                        if description:
                            break
            
            if not description:
                return None
            
            # Extract other information
            page_text = soup.get_text()
            min_amount, max_amount = self._extract_amounts(page_text)
            dates = self._extract_dates(page_text)
            contact_email = self._extract_email(page_text)
            
            grant_id = f"{source_name}_{abs(hash(title + url))}"
            
            grant_info = {
                "title": title,
                "description": description,
                "source": source_name,
                "source_url": url,
                "amount_min": min_amount,
                "amount_max": max_amount,
                "open_date": dates.get("open_date"),
                "deadline": dates.get("deadline"),
                "contact_email": contact_email,
                "industry_focus": self._determine_industry_focus(title + " " + description),
                "location": "Australia",
                "eligibility_criteria": self._extract_eligibility(page_text),
                "org_type": self._extract_org_types(page_text),
                "status": "open",
                "scraped_at": datetime.now().isoformat(),
                "grant_id": grant_id
            }
            
            return grant_info
            
        except Exception as e:
            logger.error(f"Error extracting main grant info: {str(e)}")
            return None
    
    def _extract_amounts(self, text: str) -> tuple:
        """Extract minimum and maximum amounts from text."""
        min_amount = None
        max_amount = None
        
        try:
            # Look for various amount patterns
            amount_patterns = [
                r'\$([0-9,]+(?:\.[0-9]{2})?)',
                r'([0-9,]+(?:\.[0-9]{2})?) dollars',
                r'up to \$([0-9,]+)',
                r'maximum \$([0-9,]+)',
                r'minimum \$([0-9,]+)',
                r'between \$([0-9,]+) and \$([0-9,]+)',
                r'from \$([0-9,]+) to \$([0-9,]+)',
                r'\$([0-9,]+) - \$([0-9,]+)',
                r'\$([0-9,]+) to \$([0-9,]+)'
            ]
            
            for pattern in amount_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if isinstance(match, tuple):
                            # Range pattern
                            amounts = [self._parse_amount(m) for m in match if m]
                            if amounts:
                                min_amount = min(amounts)
                                max_amount = max(amounts)
                        else:
                            # Single amount
                            amount = self._parse_amount(match)
                            if amount:
                                if 'up to' in text.lower() or 'maximum' in text.lower():
                                    max_amount = amount
                                elif 'minimum' in text.lower():
                                    min_amount = amount
                                else:
                                    max_amount = amount
                        break
                if min_amount or max_amount:
                    break
                    
        except Exception as e:
            logger.error(f"Error extracting amounts: {str(e)}")
        
        return min_amount, max_amount
    
    def _parse_amount(self, amount_str: str) -> Optional[int]:
        """Parse amount string to integer."""
        if not amount_str:
            return None
        try:
            # Remove commas and convert to int
            return int(amount_str.replace(',', ''))
        except (ValueError, TypeError):
            return None
    
    def _extract_dates(self, text: str) -> Dict[str, Optional[str]]:
        """Extract open and deadline dates from text."""
        dates = {"open_date": None, "deadline": None}
        
        try:
            # Date patterns
            date_patterns = [
                r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',
                r'(\d{1,2}) ([A-Za-z]+) (\d{4})',
                r'([A-Za-z]+) (\d{1,2}),? (\d{4})',
                r'(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})'
            ]
            
            # Look for deadline indicators
            deadline_indicators = ['deadline', 'closes', 'due', 'expires', 'ends']
            opening_indicators = ['opens', 'starts', 'begins', 'available from']
            
            for pattern in date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    date_str = ' '.join(match)
                    # Try to parse the date
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        # Determine if it's an opening or closing date based on context
                        context = self._get_date_context(text, date_str)
                        if any(indicator in context.lower() for indicator in deadline_indicators):
                            dates["deadline"] = parsed_date
                        elif any(indicator in context.lower() for indicator in opening_indicators):
                            dates["open_date"] = parsed_date
                        elif not dates["deadline"]:  # Default to deadline if not specified
                            dates["deadline"] = parsed_date
                        break
                        
        except Exception as e:
            logger.error(f"Error extracting dates: {str(e)}")
        
        return dates
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format."""
        if not date_str:
            return None
        
        try:
            # Common date formats
            formats = [
                "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d",
                "%d-%m-%Y", "%m-%d-%Y", "%Y-%m-%d",
                "%d %B %Y", "%B %d %Y", "%B %d, %Y",
                "%d %b %Y", "%b %d %Y", "%b %d, %Y"
            ]
            
            for fmt in formats:
                try:
                    parsed = datetime.strptime(date_str, fmt)
                    return parsed.strftime("%Y-%m-%d")
                except ValueError:
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
        
        return None
    
    def _get_date_context(self, text: str, date_str: str) -> str:
        """Get surrounding context for a date string."""
        try:
            index = text.find(date_str)
            if index != -1:
                start = max(0, index - 100)
                end = min(len(text), index + len(date_str) + 100)
                return text[start:end]
        except Exception:
            pass
        return ""
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        try:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            matches = re.findall(email_pattern, text)
            return matches[0] if matches else None
        except Exception as e:
            logger.error(f"Error extracting email: {str(e)}")
        return None
    
    def _determine_industry_focus(self, text: str) -> str:
        """Determine industry focus based on text content."""
        text_lower = text.lower()
        
        # Industry keywords mapping
        industry_keywords = {
            "media": ["media", "film", "television", "tv", "screen", "video", "cinema", "documentary"],
            "creative_arts": ["arts", "creative", "culture", "cultural", "artist", "performance", "theatre", "music"],
            "digital": ["digital", "online", "web", "technology", "tech", "software", "app", "game"],
            "writing": ["writing", "literature", "book", "author", "publishing", "poetry", "script"],
            "visual_arts": ["visual", "painting", "sculpture", "gallery", "exhibition", "design"],
            "music": ["music", "musician", "band", "album", "recording", "sound", "audio"],
            "other": []
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry
        
        return "other"
    
    def _extract_eligibility(self, text: str) -> List[str]:
        """Extract eligibility criteria from text."""
        criteria = []
        
        try:
            # Look for eligibility sections
            eligibility_patterns = [
                r'eligibility[^.]*',
                r'who can apply[^.]*',
                r'requirements[^.]*',
                r'criteria[^.]*'
            ]
            
            for pattern in eligibility_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    # Clean up the match
                    clean_match = re.sub(r'\s+', ' ', match.strip())
                    if clean_match and len(clean_match) > 10:
                        criteria.append(clean_match[:200])  # Limit length
                        
        except Exception as e:
            logger.error(f"Error extracting eligibility: {str(e)}")
        
        return criteria[:3]  # Return top 3 criteria
    
    def _extract_org_types(self, text: str) -> List[str]:
        """Extract organization types from text."""
        org_types = []
        text_lower = text.lower()
        
        type_keywords = {
            "small_business": ["small business", "sme", "small to medium enterprise"],
            "not_for_profit": ["not for profit", "non-profit", "nfp", "charity", "charitable"],
            "individual": ["individual", "person", "artist", "freelancer"],
            "startup": ["startup", "start-up", "new business"],
            "social_enterprise": ["social enterprise", "social impact"],
            "corporation": ["corporation", "company", "business", "enterprise"],
            "government": ["government", "council", "authority", "department"],
            "educational": ["school", "university", "college", "education"]
        }
        
        for org_type, keywords in type_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                org_types.append(org_type)
        
        return org_types if org_types else ["any"]