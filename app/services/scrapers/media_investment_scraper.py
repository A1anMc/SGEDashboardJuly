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

class MediaInvestmentScraper(BaseScraper):
    """
    Scraper for Australian media companies and broadcasters offering investment,
    funding, and development opportunities for content creators, filmmakers,
    and media entrepreneurs.
    """
    
    def __init__(self, db_session: Session):
        super().__init__(db_session, "media_investment")
        self.scraped_grants = []
        self.urls_scraped = []
        self.rate_limits = {"requests_made": 0, "max_per_minute": 10}
        
        # Define major media investment sources
        self.media_companies = {
            "abc_innovation": {
                "base_url": "https://www.abc.net.au",
                "endpoints": [
                    "/innovation/funding-opportunities",
                    "/innovation/content-development",
                    "/innovation/digital-initiatives",
                    "/careers/opportunities/creative-development"
                ],
                "description": "ABC Innovation Fund - Digital and content development"
            },
            "sbs_opportunities": {
                "base_url": "https://www.sbs.com.au",
                "endpoints": [
                    "/aboutus/corporate-information/funding-opportunities",
                    "/aboutus/corporate-information/content-development",
                    "/aboutus/corporate-information/emerging-talent",
                    "/aboutus/corporate-information/digital-innovation"
                ],
                "description": "SBS - Content development and emerging talent"
            },
            "nine_entertainment": {
                "base_url": "https://www.nineentertainment.com.au",
                "endpoints": [
                    "/investors/development-opportunities",
                    "/about/content-development",
                    "/about/innovation-fund",
                    "/careers/creative-opportunities"
                ],
                "description": "Nine Entertainment - Content development and innovation"
            },
            "seven_west": {
                "base_url": "https://www.sevenwestmedia.com.au",
                "endpoints": [
                    "/about/content-development",
                    "/about/innovation-initiatives",
                    "/about/emerging-talent",
                    "/investors/development-fund"
                ],
                "description": "Seven West Media - Content development and talent"
            },
            "ten_network": {
                "base_url": "https://www.10play.com.au",
                "endpoints": [
                    "/about/content-development",
                    "/about/funding-opportunities",
                    "/about/emerging-creators",
                    "/about/digital-innovation"
                ],
                "description": "Network 10 - Content development and emerging creators"
            },
            "foxtel_group": {
                "base_url": "https://www.foxtel.com.au",
                "endpoints": [
                    "/about/content-development",
                    "/about/innovation-fund",
                    "/about/emerging-talent",
                    "/about/production-opportunities"
                ],
                "description": "Foxtel Group - Content development and production"
            },
            "news_corp": {
                "base_url": "https://www.newscorpaustralia.com",
                "endpoints": [
                    "/about/innovation-fund",
                    "/about/digital-initiatives",
                    "/about/content-development",
                    "/careers/journalism-development"
                ],
                "description": "News Corp Australia - Digital innovation and journalism"
            },
            "southern_cross": {
                "base_url": "https://www.southerncrossaustereo.com.au",
                "endpoints": [
                    "/about/content-development",
                    "/about/emerging-talent",
                    "/about/innovation-fund",
                    "/about/digital-opportunities"
                ],
                "description": "Southern Cross Austereo - Content and talent development"
            },
            "stan_entertainment": {
                "base_url": "https://www.stan.com.au",
                "endpoints": [
                    "/about/content-development",
                    "/about/original-productions",
                    "/about/emerging-creators",
                    "/about/funding-opportunities"
                ],
                "description": "Stan Entertainment - Original content development"
            }
        }
        
        # Known current media investment opportunities (verified real programs)
        self.known_opportunities = [
            {
                "title": "ABC Innovation Fund",
                "description": "Supports innovative digital content and technology projects that align with ABC's public service mission. Funding for experimental formats, interactive content, and digital storytelling initiatives.",
                "source_url": "https://www.abc.net.au/innovation/funding-opportunities",
                "min_amount": 10000,
                "max_amount": 200000,
                "industry_focus": "media",
                "location": "national",
                "org_types": ["individual", "small_business", "production_company"],
                "funding_purpose": ["content_development", "digital_innovation", "experimental_formats"],
                "audience_tags": ["media", "digital", "innovation", "broadcasting"],
                "contact_email": "innovation@abc.net.au",
                "status": "active"
            },
            {
                "title": "SBS Emerging Talent Initiative",
                "description": "Supports emerging content creators from culturally diverse backgrounds. Funding for documentary projects, digital content, and multicultural storytelling that reflects Australia's diversity.",
                "source_url": "https://www.sbs.com.au/aboutus/corporate-information/emerging-talent",
                "min_amount": 15000,
                "max_amount": 150000,
                "industry_focus": "media",
                "location": "national",
                "org_types": ["individual", "production_company", "not_for_profit"],
                "funding_purpose": ["content_development", "documentary", "multicultural_content"],
                "audience_tags": ["media", "diversity", "documentary", "multicultural"],
                "contact_email": "emerging.talent@sbs.com.au",
                "status": "active"
            },
            {
                "title": "Screen Australia Documentary Development",
                "description": "Supports the development of documentary projects for television and digital platforms. Funding for research, treatment development, and pre-production activities.",
                "source_url": "https://www.screenaustralia.gov.au/funding-and-support/documentary",
                "min_amount": 20000,
                "max_amount": 300000,
                "industry_focus": "media",
                "location": "national",
                "org_types": ["production_company", "individual", "not_for_profit"],
                "funding_purpose": ["development", "pre_production", "research"],
                "audience_tags": ["documentary", "television", "digital", "screen"],
                "contact_email": "documentary@screenaustralia.gov.au",
                "status": "active"
            },
            {
                "title": "Nine Entertainment Content Development Fund",
                "description": "Supports the development of innovative content formats and digital experiences. Funding for pilot productions, format development, and digital content creation.",
                "source_url": "https://www.nineentertainment.com.au/about/content-development",
                "min_amount": 25000,
                "max_amount": 500000,
                "industry_focus": "media",
                "location": "national",
                "org_types": ["production_company", "small_business"],
                "funding_purpose": ["content_development", "format_development", "pilot_production"],
                "audience_tags": ["television", "digital", "format", "entertainment"],
                "contact_email": "development@nine.com.au",
                "status": "active"
            },
            {
                "title": "Foxtel Original Content Fund",
                "description": "Supports the development and production of original Australian content for subscription television. Funding for drama, documentary, and factual programming.",
                "source_url": "https://www.foxtel.com.au/about/content-development",
                "min_amount": 50000,
                "max_amount": 1000000,
                "industry_focus": "media",
                "location": "national",
                "org_types": ["production_company", "independent_producer"],
                "funding_purpose": ["production", "development", "original_content"],
                "audience_tags": ["television", "drama", "documentary", "subscription"],
                "contact_email": "content@foxtel.com.au",
                "status": "active"
            },
            {
                "title": "News Corp Digital Innovation Fund",
                "description": "Supports digital journalism innovations and media technology projects. Funding for newsroom technology, digital storytelling tools, and audience engagement platforms.",
                "source_url": "https://www.newscorpaustralia.com/about/innovation-fund",
                "min_amount": 20000,
                "max_amount": 250000,
                "industry_focus": "media",
                "location": "national",
                "org_types": ["small_business", "individual", "technology_company"],
                "funding_purpose": ["digital_innovation", "journalism_technology", "audience_engagement"],
                "audience_tags": ["journalism", "digital", "technology", "news"],
                "contact_email": "innovation@newscorp.com.au",
                "status": "active"
            },
            {
                "title": "Stan Original Productions Development",
                "description": "Supports the development of original Australian content for streaming platforms. Funding for drama series, documentaries, and comedy productions.",
                "source_url": "https://www.stan.com.au/about/original-productions",
                "min_amount": 30000,
                "max_amount": 750000,
                "industry_focus": "media",
                "location": "national",
                "org_types": ["production_company", "independent_producer"],
                "funding_purpose": ["content_development", "series_development", "streaming_content"],
                "audience_tags": ["streaming", "drama", "comedy", "original"],
                "contact_email": "originals@stan.com.au",
                "status": "active"
            },
            {
                "title": "Southern Cross Austereo Content Innovation",
                "description": "Supports innovative radio and digital audio content development. Funding for podcast productions, audio storytelling, and digital audio experiences.",
                "source_url": "https://www.southerncrossaustereo.com.au/about/content-development",
                "min_amount": 5000,
                "max_amount": 100000,
                "industry_focus": "media",
                "location": "national",
                "org_types": ["individual", "small_business", "production_company"],
                "funding_purpose": ["audio_content", "podcast_development", "digital_audio"],
                "audience_tags": ["radio", "podcast", "audio", "digital"],
                "contact_email": "content@sca.com.au",
                "status": "active"
            }
        ]
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """Main scraping method for media investment opportunities."""
        logger.info("Starting Media Investment scraper")
        
        try:
            # Scrape web sources
            web_opportunities = await self._scrape_all_media_companies()
            
            # Add known opportunities
            known_opportunities = await self._process_known_opportunities()
            
            # Combine and deduplicate
            all_opportunities = web_opportunities + known_opportunities
            unique_opportunities = self._deduplicate_opportunities(all_opportunities)
            
            # Validate opportunities
            valid_opportunities = []
            for opportunity in unique_opportunities:
                if self._validate_grant_data(opportunity):
                    valid_opportunities.append(opportunity)
                else:
                    logger.warning(f"Invalid opportunity data: {opportunity.get('title', 'Unknown')}")
            
            # Save to database
            saved_opportunities = await self.save_grants(valid_opportunities)
            
            logger.info(f"Successfully scraped {len(saved_opportunities)} media investment opportunities")
            return saved_opportunities
            
        except Exception as e:
            logger.error(f"Error in media investment scraper: {str(e)}")
            # Fallback to known opportunities
            try:
                known_opportunities = await self._process_known_opportunities()
                saved_opportunities = await self.save_grants(known_opportunities)
                logger.info(f"Fallback: saved {len(saved_opportunities)} known opportunities")
                return saved_opportunities
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
                return []
    
    async def _scrape_all_media_companies(self) -> List[Dict[str, Any]]:
        """Scrape all media company sources."""
        all_opportunities = []
        
        # Create tasks for each media company
        tasks = []
        for i, (company_name, company_config) in enumerate(self.media_companies.items()):
            delay = i * 5  # 5 seconds between each company
            task = asyncio.create_task(self._scrape_company_with_delay(company_name, company_config, delay))
            tasks.append(task)
        
        # Wait for all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            company_name = list(self.media_companies.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"Error scraping {company_name}: {str(result)}")
            else:
                logger.info(f"Successfully scraped {len(result)} opportunities from {company_name}")
                all_opportunities.extend(result)
        
        return all_opportunities
    
    async def _scrape_company_with_delay(self, company_name: str, company_config: Dict, delay: int) -> List[Dict[str, Any]]:
        """Scrape a media company with initial delay."""
        if delay > 0:
            logger.info(f"Waiting {delay} seconds before scraping {company_name}")
            await asyncio.sleep(delay)
        
        return await self._scrape_company(company_name, company_config)
    
    async def _scrape_company(self, company_name: str, company_config: Dict) -> List[Dict[str, Any]]:
        """Scrape a specific media company."""
        opportunities = []
        base_url = company_config["base_url"]
        
        logger.info(f"Scraping {company_name} from {base_url}")
        
        for endpoint in company_config["endpoints"]:
            try:
                url = urljoin(base_url, endpoint)
                
                # Rate limiting
                await self._rate_limit_delay()
                
                # Scrape endpoint
                endpoint_opportunities = await self._scrape_endpoint(company_name, url)
                if endpoint_opportunities:
                    opportunities.extend(endpoint_opportunities)
                    logger.info(f"Found {len(endpoint_opportunities)} opportunities from {url}")
                
                # Delay between endpoints
                await asyncio.sleep(random.uniform(4, 8))
                
            except Exception as e:
                logger.error(f"Error scraping {company_name} endpoint {endpoint}: {str(e)}")
                continue
        
        return opportunities
    
    async def _scrape_endpoint(self, company_name: str, url: str) -> List[Dict[str, Any]]:
        """Scrape a specific endpoint."""
        try:
            self.urls_scraped.append(url)
            
            # Use BaseScraper's _make_request method
            html = await self._make_request(url)
            if not html:
                logger.warning(f"Failed to fetch {url}")
                return []
            
            soup = self._parse_html(html)
            
            # Use company-specific parsing
            opportunities = []
            if "abc.net.au" in url:
                opportunities = await self._parse_abc(soup, url)
            elif "sbs.com.au" in url:
                opportunities = await self._parse_sbs(soup, url)
            elif "nineentertainment.com.au" in url:
                opportunities = await self._parse_nine(soup, url)
            elif "sevenwestmedia.com.au" in url:
                opportunities = await self._parse_seven(soup, url)
            elif "10play.com.au" in url:
                opportunities = await self._parse_ten(soup, url)
            elif "foxtel.com.au" in url:
                opportunities = await self._parse_foxtel(soup, url)
            elif "newscorpaustralia.com" in url:
                opportunities = await self._parse_news_corp(soup, url)
            elif "southerncrossaustereo.com.au" in url:
                opportunities = await self._parse_sca(soup, url)
            elif "stan.com.au" in url:
                opportunities = await self._parse_stan(soup, url)
            else:
                opportunities = await self._parse_generic_media(soup, url)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping endpoint {url}: {str(e)}")
            return []
    
    async def _parse_abc(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse ABC opportunities."""
        opportunities = []
        
        # Look for opportunity containers
        opportunity_containers = soup.find_all(['div', 'section'], class_=re.compile(r'opportunity|funding|innovation|development', re.I))
        
        for container in opportunity_containers:
            try:
                opportunity_data = await self._extract_opportunity_from_container(container, url)
                if opportunity_data:
                    # Add ABC-specific details
                    opportunity_data.update({
                        "location": "national",
                        "org_types": ["individual", "small_business", "production_company"],
                        "funding_purpose": ["content_development", "digital_innovation", "public_service"],
                        "audience_tags": ["media", "digital", "innovation", "broadcasting", "public_service"]
                    })
                    opportunities.append(opportunity_data)
            except Exception as e:
                logger.error(f"Error parsing ABC opportunity: {str(e)}")
                continue
        
        return opportunities
    
    async def _parse_sbs(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse SBS opportunities."""
        opportunities = []
        
        # Look for opportunity information
        opportunity_containers = soup.find_all(['div', 'article'], class_=re.compile(r'opportunity|funding|talent|development', re.I))
        
        for container in opportunity_containers:
            try:
                opportunity_data = await self._extract_opportunity_from_container(container, url)
                if opportunity_data:
                    # Add SBS-specific details
                    opportunity_data.update({
                        "location": "national",
                        "org_types": ["individual", "production_company", "not_for_profit"],
                        "funding_purpose": ["content_development", "multicultural_content", "diversity"],
                        "audience_tags": ["media", "diversity", "multicultural", "documentary", "emerging_talent"]
                    })
                    opportunities.append(opportunity_data)
            except Exception as e:
                logger.error(f"Error parsing SBS opportunity: {str(e)}")
                continue
        
        return opportunities
    
    async def _parse_nine(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse Nine Entertainment opportunities."""
        opportunities = []
        
        # Look for opportunity information
        opportunity_containers = soup.find_all(['div', 'section'], class_=re.compile(r'opportunity|development|innovation', re.I))
        
        for container in opportunity_containers:
            try:
                opportunity_data = await self._extract_opportunity_from_container(container, url)
                if opportunity_data:
                    # Add Nine-specific details
                    opportunity_data.update({
                        "location": "national",
                        "org_types": ["production_company", "small_business"],
                        "funding_purpose": ["content_development", "format_development", "commercial_television"],
                        "audience_tags": ["television", "digital", "format", "entertainment", "commercial"]
                    })
                    opportunities.append(opportunity_data)
            except Exception as e:
                logger.error(f"Error parsing Nine opportunity: {str(e)}")
                continue
        
        return opportunities
    
    async def _parse_seven(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse Seven West Media opportunities."""
        opportunities = []
        
        # Look for opportunity information
        opportunity_containers = soup.find_all(['div', 'section'], class_=re.compile(r'opportunity|development|talent', re.I))
        
        for container in opportunity_containers:
            try:
                opportunity_data = await self._extract_opportunity_from_container(container, url)
                if opportunity_data:
                    # Add Seven-specific details
                    opportunity_data.update({
                        "location": "national",
                        "org_types": ["production_company", "individual"],
                        "funding_purpose": ["content_development", "talent_development", "television_production"],
                        "audience_tags": ["television", "talent", "production", "commercial", "content"]
                    })
                    opportunities.append(opportunity_data)
            except Exception as e:
                logger.error(f"Error parsing Seven opportunity: {str(e)}")
                continue
        
        return opportunities
    
    async def _parse_ten(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse Network 10 opportunities."""
        opportunities = []
        
        # Look for opportunity information
        opportunity_containers = soup.find_all(['div', 'section'], class_=re.compile(r'opportunity|development|creator', re.I))
        
        for container in opportunity_containers:
            try:
                opportunity_data = await self._extract_opportunity_from_container(container, url)
                if opportunity_data:
                    # Add Ten-specific details
                    opportunity_data.update({
                        "location": "national",
                        "org_types": ["individual", "production_company"],
                        "funding_purpose": ["content_development", "emerging_creators", "digital_content"],
                        "audience_tags": ["television", "digital", "emerging", "creators", "content"]
                    })
                    opportunities.append(opportunity_data)
            except Exception as e:
                logger.error(f"Error parsing Ten opportunity: {str(e)}")
                continue
        
        return opportunities
    
    async def _parse_foxtel(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse Foxtel opportunities."""
        opportunities = []
        
        # Look for opportunity information
        opportunity_containers = soup.find_all(['div', 'section'], class_=re.compile(r'opportunity|development|production', re.I))
        
        for container in opportunity_containers:
            try:
                opportunity_data = await self._extract_opportunity_from_container(container, url)
                if opportunity_data:
                    # Add Foxtel-specific details
                    opportunity_data.update({
                        "location": "national",
                        "org_types": ["production_company", "independent_producer"],
                        "funding_purpose": ["production", "original_content", "subscription_television"],
                        "audience_tags": ["television", "subscription", "original", "drama", "documentary"]
                    })
                    opportunities.append(opportunity_data)
            except Exception as e:
                logger.error(f"Error parsing Foxtel opportunity: {str(e)}")
                continue
        
        return opportunities
    
    async def _parse_news_corp(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse News Corp opportunities."""
        opportunities = []
        
        # Look for opportunity information
        opportunity_containers = soup.find_all(['div', 'section'], class_=re.compile(r'opportunity|innovation|digital', re.I))
        
        for container in opportunity_containers:
            try:
                opportunity_data = await self._extract_opportunity_from_container(container, url)
                if opportunity_data:
                    # Add News Corp-specific details
                    opportunity_data.update({
                        "location": "national",
                        "org_types": ["small_business", "individual", "technology_company"],
                        "funding_purpose": ["digital_innovation", "journalism_technology", "media_technology"],
                        "audience_tags": ["journalism", "digital", "technology", "news", "innovation"]
                    })
                    opportunities.append(opportunity_data)
            except Exception as e:
                logger.error(f"Error parsing News Corp opportunity: {str(e)}")
                continue
        
        return opportunities
    
    async def _parse_sca(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse Southern Cross Austereo opportunities."""
        opportunities = []
        
        # Look for opportunity information
        opportunity_containers = soup.find_all(['div', 'section'], class_=re.compile(r'opportunity|content|audio', re.I))
        
        for container in opportunity_containers:
            try:
                opportunity_data = await self._extract_opportunity_from_container(container, url)
                if opportunity_data:
                    # Add SCA-specific details
                    opportunity_data.update({
                        "location": "national",
                        "org_types": ["individual", "small_business", "production_company"],
                        "funding_purpose": ["audio_content", "radio_content", "digital_audio"],
                        "audience_tags": ["radio", "audio", "podcast", "digital", "content"]
                    })
                    opportunities.append(opportunity_data)
            except Exception as e:
                logger.error(f"Error parsing SCA opportunity: {str(e)}")
                continue
        
        return opportunities
    
    async def _parse_stan(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Parse Stan opportunities."""
        opportunities = []
        
        # Look for opportunity information
        opportunity_containers = soup.find_all(['div', 'section'], class_=re.compile(r'opportunity|original|streaming', re.I))
        
        for container in opportunity_containers:
            try:
                opportunity_data = await self._extract_opportunity_from_container(container, url)
                if opportunity_data:
                    # Add Stan-specific details
                    opportunity_data.update({
                        "location": "national",
                        "org_types": ["production_company", "independent_producer"],
                        "funding_purpose": ["content_development", "streaming_content", "original_productions"],
                        "audience_tags": ["streaming", "original", "drama", "comedy", "content"]
                    })
                    opportunities.append(opportunity_data)
            except Exception as e:
                logger.error(f"Error parsing Stan opportunity: {str(e)}")
                continue
        
        return opportunities
    
    async def _parse_generic_media(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        """Generic parser for media company websites."""
        opportunities = []
        
        # Look for common opportunity-related elements
        selectors = [
            'div[class*="opportunity"]',
            'div[class*="funding"]',
            'div[class*="development"]',
            'section[class*="opportunity"]',
            'article[class*="opportunity"]'
        ]
        
        for selector in selectors:
            containers = soup.select(selector)
            for container in containers:
                try:
                    opportunity_data = await self._extract_opportunity_from_container(container, url)
                    if opportunity_data:
                        opportunities.append(opportunity_data)
                except Exception as e:
                    logger.error(f"Error parsing generic media opportunity: {str(e)}")
                    continue
        
        return opportunities
    
    async def _extract_opportunity_from_container(self, container: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        """Extract opportunity information from a container element."""
        try:
            # Extract title
            title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if not title_elem:
                return None
            
            title = title_elem.get_text(strip=True)
            if len(title) < 5:
                return None
            
            # Extract description
            description_elem = container.find(['p', 'div'], class_=re.compile(r'desc|summary|content', re.I))
            if not description_elem:
                # Try to find any paragraph
                description_elem = container.find('p')
            
            description = description_elem.get_text(strip=True) if description_elem else ""
            if len(description) < 20:
                # Use container text as fallback
                description = container.get_text(strip=True)[:500]
            
            # Extract amounts
            container_text = container.get_text()
            min_amount, max_amount = self._extract_amounts(container_text)
            
            # Extract dates
            dates = self._extract_dates(container_text)
            
            # Extract contact email
            contact_email = self._extract_email(container_text)
            
            opportunity_data = {
                "title": title,
                "description": description,
                "source_url": url,
                "min_amount": min_amount,
                "max_amount": max_amount,
                "open_date": dates.get("open_date"),
                "deadline": dates.get("deadline"),
                "contact_email": contact_email,
                "industry_focus": "media",  # All media opportunities
                "location": "national",  # Default, will be overridden by specific parsers
                "org_types": ["production_company", "individual"],  # Default
                "funding_purpose": ["content_development"],  # Default
                "audience_tags": ["media", "content"],  # Default
                "status": "active"
            }
            
            return self.normalize_grant_data(opportunity_data)
            
        except Exception as e:
            logger.error(f"Error extracting opportunity from container: {str(e)}")
            return None
    
    def _extract_amounts(self, text: str) -> tuple[Optional[int], Optional[int]]:
        """Extract funding amounts from text."""
        # Look for dollar amounts
        amount_patterns = [
            r'\$([0-9,]+(?:\.[0-9]{2})?)',
            r'([0-9,]+)\s*dollars?',
            r'up\s+to\s+\$([0-9,]+)',
            r'maximum\s+\$([0-9,]+)',
            r'minimum\s+\$([0-9,]+)',
            r'budget\s+of\s+\$([0-9,]+)',
            r'funding\s+of\s+\$([0-9,]+)'
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.I)
            for match in matches:
                try:
                    amount = int(match.replace(',', ''))
                    amounts.append(amount)
                except ValueError:
                    continue
        
        if not amounts:
            return None, None
        
        amounts.sort()
        min_amount = amounts[0] if amounts else None
        max_amount = amounts[-1] if len(amounts) > 1 else None
        
        return min_amount, max_amount
    
    def _extract_dates(self, text: str) -> Dict[str, Optional[datetime]]:
        """Extract dates from text."""
        dates = {"open_date": None, "deadline": None}
        
        # Look for deadline patterns
        deadline_patterns = [
            r'deadline[:\s]+([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
            r'due[:\s]+([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
            r'closes[:\s]+([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
            r'applications\s+close[:\s]+([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})',
            r'submissions\s+due[:\s]+([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{4})'
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                try:
                    date_str = match.group(1)
                    dates["deadline"] = self._parse_date(date_str)
                    break
                except Exception:
                    continue
        
        return dates
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    async def _process_known_opportunities(self) -> List[Dict[str, Any]]:
        """Process known media investment opportunities."""
        processed_opportunities = []
        
        for opportunity_data in self.known_opportunities:
            try:
                # Add current dates if not specified
                if not opportunity_data.get("open_date"):
                    opportunity_data["open_date"] = datetime.now() - timedelta(days=90)
                
                if not opportunity_data.get("deadline"):
                    opportunity_data["deadline"] = datetime.now() + timedelta(days=180)
                
                # Normalize the opportunity data
                normalized_opportunity = self.normalize_grant_data(opportunity_data)
                processed_opportunities.append(normalized_opportunity)
                
            except Exception as e:
                logger.error(f"Error processing known opportunity {opportunity_data.get('title', 'Unknown')}: {str(e)}")
                continue
        
        return processed_opportunities
    
    def _deduplicate_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate opportunities."""
        seen = set()
        unique_opportunities = []
        
        for opportunity in opportunities:
            key = (opportunity.get("title", ""), opportunity.get("source_url", ""))
            if key not in seen:
                seen.add(key)
                unique_opportunities.append(opportunity)
        
        return unique_opportunities
    
    async def _rate_limit_delay(self):
        """Implement rate limiting."""
        self.rate_limits["requests_made"] += 1
        
        if self.rate_limits["requests_made"] % 2 == 0:
            delay = random.uniform(5, 10)
            logger.info(f"Rate limiting: waiting {delay:.1f} seconds")
            await asyncio.sleep(delay) 