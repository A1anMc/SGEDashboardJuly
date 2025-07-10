import asyncio
import logging
import random
from typing import List, Dict, Optional, Any
from datetime import datetime
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
        
        # Define target sources with their configurations
        self.sources = {
            "screen_australia": {
                "base_url": "https://www.screenaustralia.gov.au",
                "endpoints": [
                    "/funding-and-support/narrative-content-development",
                    "/funding-and-support/narrative-content-production",
                    "/funding-and-support/documentary",
                    "/funding-and-support/games"
                ],
                "description": "Screen Australia - Government funding for screen content"
            },
            "creative_australia": {
                "base_url": "https://creative.gov.au",
                "endpoints": [
                    "/investment-and-development/arts-projects-for-individuals-and-groups",
                    "/investment-and-development/arts-projects-for-organisations"
                ],
                "description": "Creative Australia - Federal arts funding"
            },
            "business_gov": {
                "base_url": "https://business.gov.au",
                "endpoints": [
                    "/grants-and-programs/arts-and-culture",
                    "/grants-and-programs/creative-industries"
                ],
                "description": "Business.gov.au - Creative industry grants"
            },
            "create_nsw": {
                "base_url": "https://www.create.nsw.gov.au",
                "endpoints": [
                    "/funding-and-support/organisations",
                    "/funding-and-support/individuals"
                ],
                "description": "Create NSW - NSW state government arts funding"
            }
        }
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method that coordinates all source scraping."""
        logger.info("Starting Australian grants scraper")
        
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
        """Scrape a specific source using the BaseScraper _make_request method."""
        grants = []
        base_url = source_config["base_url"]
        
        for endpoint in source_config["endpoints"]:
            try:
                url = urljoin(base_url, endpoint)
                
                # Add random delay between requests
                await asyncio.sleep(random.uniform(1, 2))
                
                # Use BaseScraper's _make_request method
                html = await self._make_request(url)
                if not html:
                    logger.warning(f"Failed to fetch {url}")
                    continue
                
                soup = self._parse_html(html)
                
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
            
            # Also check for main content
            if not grants:
                main_grant = await self._extract_main_grant_info(soup, url, "Screen Australia")
                if main_grant:
                    grants.append(main_grant)
                    
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
            
            # Check for main content if no specific grants found
            if not grants:
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
            
            # Check for main content if no specific grants found
            if not grants:
                main_grant = await self._extract_main_grant_info(soup, url, "Business.gov.au")
                if main_grant:
                    grants.append(main_grant)
                    
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
            
            # Check for main content if no specific grants found
            if not grants:
                main_grant = await self._extract_main_grant_info(soup, url, "Create NSW")
                if main_grant:
                    grants.append(main_grant)
                    
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
            
            # Check for main content if no specific grants found
            if not grants:
                main_grant = await self._extract_main_grant_info(soup, url, "Australian Government")
                if main_grant:
                    grants.append(main_grant)
                    
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
                "min_amount": min_amount,  # Already a number or None
                "max_amount": max_amount,  # Already a number or None
                "open_date": dates.get("open_date"),
                "deadline": dates.get("deadline"),
                "contact_email": contact_email or "",
                "industry_focus": self._determine_industry_focus(title + " " + description),
                "location": "national",
                "org_types": self._extract_org_types(element_text),
                "funding_purpose": self._extract_funding_purpose(title + " " + description),
                "audience_tags": self._extract_audience_tags(title + " " + description)
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
                return None
                
            title = title_element.get_text(strip=True)
            
            # Skip if title is too short
            if len(title) < 10:
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
                "min_amount": min_amount,  # Already a number or None
                "max_amount": max_amount,  # Already a number or None
                "open_date": dates.get("open_date"),
                "deadline": dates.get("deadline"),
                "contact_email": contact_email or "",
                "industry_focus": self._determine_industry_focus(title + " " + description),
                "location": "national",
                "org_types": self._extract_org_types(page_text),
                "funding_purpose": self._extract_funding_purpose(title + " " + description),
                "audience_tags": self._extract_audience_tags(title + " " + description)
            }
            
            # Use BaseScraper's normalize_grant_data method
            return self.normalize_grant_data(grant_data)
            
        except Exception as e:
            logger.error(f"Error extracting main grant info: {str(e)}")
            return None
    
    def _extract_description(self, element: BeautifulSoup) -> Optional[str]:
        """Extract description from an element."""
        # Look for description in various ways
        description_elements = element.find_all(['p', 'div'], class_=re.compile(r'description|summary|overview'))
        for desc_elem in description_elements:
            desc_text = desc_elem.get_text(strip=True)
            if desc_text and len(desc_text) > 20:
                return desc_text[:500] + "..." if len(desc_text) > 500 else desc_text
        
        # Fallback to getting text from paragraphs
        paragraphs = element.find_all('p')
        for p in paragraphs[:3]:  # Check first 3 paragraphs
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                return text[:500] + "..." if len(text) > 500 else text
        
        return None
    
    def _extract_page_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract description from the main page content."""
        # Look for meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            description = meta_desc.get('content', '')
            if description and len(description) > 20:
                return description
        
        # Look for main content
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
                        return text[:500] + "..." if len(text) > 500 else text
        
        return None
    
    def _extract_amounts(self, text: str) -> tuple:
        """Extract minimum and maximum amounts from text, returning numbers."""
        min_amount = None
        max_amount = None
        
        try:
            # Look for various amount patterns
            amount_patterns = [
                r'up to \$([0-9,]+)',
                r'maximum \$([0-9,]+)',
                r'minimum \$([0-9,]+)',
                r'between \$([0-9,]+) and \$([0-9,]+)',
                r'from \$([0-9,]+) to \$([0-9,]+)',
                r'\$([0-9,]+) - \$([0-9,]+)',
                r'\$([0-9,]+) to \$([0-9,]+)',
                r'\$([0-9,]+(?:\.[0-9]{2})?)',
            ]
            
            for pattern in amount_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if isinstance(match, tuple):
                            # Range pattern
                            amounts = [self._parse_amount(m) for m in match if m]
                            amounts = [a for a in amounts if a is not None]
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
                if min_amount is not None or max_amount is not None:
                    break
                    
        except Exception as e:
            logger.error(f"Error extracting amounts: {str(e)}")
        
        return min_amount, max_amount
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string to float (compatible with Numeric(10,2) database field)."""
        if not amount_str:
            return None
        try:
            # Remove commas and convert to float
            cleaned = amount_str.replace(',', '').replace('$', '')
            return float(cleaned)
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
                    # Try to parse the date using BaseScraper's method
                    parsed_date = self._parse_date(date_str)
                    if parsed_date:
                        # Determine if it's an opening or closing date based on context
                        context = self._get_date_context(text, date_str)
                        if any(indicator in context.lower() for indicator in deadline_indicators):
                            dates["deadline"] = parsed_date.strftime("%Y-%m-%d")
                        elif any(indicator in context.lower() for indicator in opening_indicators):
                            dates["open_date"] = parsed_date.strftime("%Y-%m-%d")
                        elif not dates["deadline"]:  # Default to deadline if not specified
                            dates["deadline"] = parsed_date.strftime("%Y-%m-%d")
                        break
                        
        except Exception as e:
            logger.error(f"Error extracting dates: {str(e)}")
        
        return dates
    
    def _get_date_context(self, text: str, date_str: str) -> str:
        """Get context around a date string."""
        try:
            index = text.find(date_str)
            if index == -1:
                return ""
            
            # Get 50 characters before and after
            start = max(0, index - 50)
            end = min(len(text), index + len(date_str) + 50)
            return text[start:end]
        except Exception:
            return ""
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        try:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            matches = re.findall(email_pattern, text)
            return matches[0] if matches else None
        except Exception:
            return None
    
    def _determine_industry_focus(self, text: str) -> str:
        """Determine industry focus based on text content."""
        text_lower = text.lower()
        
        # Industry keywords mapping
        industry_keywords = {
            "media": ["screen", "film", "television", "tv", "media", "video", "documentary", "production"],
            "creative_arts": ["arts", "creative", "culture", "music", "visual", "performing", "theatre", "dance"],
            "digital": ["digital", "technology", "tech", "software", "app", "website", "online", "gaming", "games"]
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry
        
        # Check for business keywords last, as they might be too generic
        business_keywords = ["business", "entrepreneurship", "startup", "commercial", "export", "trade"]
        if any(keyword in text_lower for keyword in business_keywords) and not any(
            keyword in text_lower for keywords in industry_keywords.values() for keyword in keywords
        ):
            return "business"
        
        return "other"
    
    def _extract_org_types(self, text: str) -> List[str]:
        """Extract organization types from text."""
        text_lower = text.lower()
        org_types = []
        
        type_keywords = {
            "individual": ["individual", "person", "artist", "freelancer"],
            "small_business": ["small business", "sme", "startup", "entrepreneur"],
            "not_for_profit": ["not for profit", "non profit", "nfp", "ngo", "charity"],
            "corporation": ["corporation", "company", "business", "enterprise"],
            "educational": ["university", "school", "education", "academic", "research"],
            "social_enterprise": ["social enterprise", "social business"]
        }
        
        for org_type, keywords in type_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                org_types.append(org_type)
        
        return org_types if org_types else ["any"]
    
    def _extract_funding_purpose(self, text: str) -> List[str]:
        """Extract funding purposes from text."""
        text_lower = text.lower()
        purposes = []
        
        purpose_keywords = {
            "development": ["development", "create", "build", "establish"],
            "production": ["production", "manufacture", "produce", "make"],
            "research": ["research", "study", "investigation", "analysis"],
            "marketing": ["marketing", "promotion", "advertising", "outreach"],
            "capacity_building": ["capacity", "training", "skill", "education"],
            "equipment": ["equipment", "technology", "tools", "infrastructure"]
        }
        
        for purpose, keywords in purpose_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                purposes.append(purpose)
        
        return purposes if purposes else ["general"]
    
    def _extract_audience_tags(self, text: str) -> List[str]:
        """Extract audience tags from text."""
        text_lower = text.lower()
        tags = []
        
        tag_keywords = {
            "australian": ["australian", "australia"],
            "creative": ["creative", "artist", "arts"],
            "media": ["media", "screen", "film", "television"],
            "emerging": ["emerging", "new", "early"],
            "established": ["established", "experienced", "professional"],
            "regional": ["regional", "rural", "remote"],
            "indigenous": ["indigenous", "aboriginal", "torres strait"],
            "diverse": ["diverse", "multicultural", "disability", "women"]
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)
        
        return tags if tags else ["general"]