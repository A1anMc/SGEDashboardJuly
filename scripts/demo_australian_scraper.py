#!/usr/bin/env python3
"""
Demonstration of the Australian Grants Scraper functionality

This script shows how the scraper works and what kind of data it extracts,
without requiring external dependencies like aiohttp.
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class AustralianGrantsScraperDemo:
    """
    Demonstration version of the Australian Grants Scraper
    showing the core data extraction functionality.
    """
    
    def __init__(self):
        self.sources = {
            "screen_australia": {
                "base_url": "https://www.screenaustralia.gov.au",
                "description": "Screen Australia - Government funding for screen/media content",
                "endpoints": [
                    "/funding-and-support/narrative-content-development",
                    "/funding-and-support/narrative-content-production", 
                    "/funding-and-support/documentary",
                    "/funding-and-support/games",
                    "/funding-and-support/industry-development"
                ]
            },
            "creative_australia": {
                "base_url": "https://creative.gov.au",
                "description": "Creative Australia - Federal arts funding",
                "endpoints": [
                    "/investment-and-development/arts-projects-for-individuals-and-groups",
                    "/investment-and-development/arts-projects-for-organisations",
                    "/investment-and-development/multi-year-investment"
                ]
            },
            "business_gov": {
                "base_url": "https://business.gov.au", 
                "description": "Business.gov.au - Creative industry grants",
                "endpoints": [
                    "/grants-and-programs/screen-australia-funding-and-support",
                    "/grants-and-programs/arts-and-culture",
                    "/grants-and-programs/creative-industries"
                ]
            },
            "create_nsw": {
                "base_url": "https://www.create.nsw.gov.au",
                "description": "Create NSW - NSW state government arts funding", 
                "endpoints": [
                    "/funding-and-support/organisations",
                    "/funding-and-support/individuals",
                    "/funding-and-support/quick-response"
                ]
            }
        }
    
    def extract_amounts(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract minimum and maximum amounts from text."""
        min_amount = None
        max_amount = None
        
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
        
        return min_amount, max_amount
    
    def _parse_amount(self, amount_str: str) -> Optional[int]:
        """Parse amount string to integer."""
        if not amount_str:
            return None
        try:
            return int(amount_str.replace(',', ''))
        except (ValueError, TypeError):
            return None
    
    def extract_dates(self, text: str) -> Dict[str, Optional[str]]:
        """Extract open and deadline dates from text."""
        dates = {"open_date": None, "deadline": None}
        
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
        
        return dates
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date string to ISO format."""
        if not date_str:
            return None
        
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
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None
    
    def determine_industry_focus(self, text: str) -> str:
        """Determine industry focus based on text content."""
        text_lower = text.lower()
        
        industry_keywords = {
            "media": ["media", "film", "television", "tv", "screen", "video", "cinema", "documentary"],
            "creative_arts": ["arts", "creative", "culture", "cultural", "artist", "performance", "theatre", "music"],
            "digital": ["digital", "online", "web", "technology", "tech", "software", "app", "game"],
            "writing": ["writing", "literature", "book", "author", "publishing", "poetry", "script"],
            "visual_arts": ["visual", "painting", "sculpture", "gallery", "exhibition", "design"],
            "music": ["music", "musician", "band", "album", "recording", "sound", "audio"],
        }
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry
        
        return "other"
    
    def extract_org_types(self, text: str) -> List[str]:
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

def demo_data_extraction():
    """Demonstrate the data extraction capabilities."""
    logger.info("🔍 Demonstrating Australian Grants Scraper Data Extraction")
    logger.info("=" * 60)
    
    scraper = AustralianGrantsScraperDemo()
    
    # Test amount extraction
    logger.info("\n💰 Amount Extraction Tests:")
    amount_tests = [
        "Funding up to $50,000 is available for screen projects",
        "Grants between $10,000 and $100,000 for creative industries", 
        "Maximum funding of $1,500,000 for major productions",
        "Individual grants from $5,000 to $25,000",
        "Up to $250,000 available for documentary development"
    ]
    
    for text in amount_tests:
        min_amt, max_amt = scraper.extract_amounts(text)
        logger.info(f"  📝 '{text}'")
        logger.info(f"     💵 Min: ${min_amt:,}" if min_amt else "     💵 Min: None")
        logger.info(f"     💵 Max: ${max_amt:,}" if max_amt else "     💵 Max: None")
        logger.info("")
    
    # Test date extraction  
    logger.info("\n📅 Date Extraction Tests:")
    date_tests = [
        "Applications close on 31 December 2024 for all eligible projects",
        "Program opens 15 March 2025, deadline 30 June 2025",
        "Next round closes 15/09/2024 at 5pm AEST",
        "Available from 1 January 2025 until 31 March 2025"
    ]
    
    for text in date_tests:
        dates = scraper.extract_dates(text)
        logger.info(f"  📝 '{text}'")
        logger.info(f"     📅 Open: {dates['open_date'] or 'Not found'}")
        logger.info(f"     📅 Deadline: {dates['deadline'] or 'Not found'}")
        logger.info("")
    
    # Test industry focus detection
    logger.info("\n🎯 Industry Focus Detection:")
    industry_tests = [
        "Film and television production funding for Australian creators",
        "Support for creative artists and cultural practitioners",
        "Digital technology and game development grants",
        "Music recording and album production support",
        "Visual arts exhibition and gallery funding",
        "General business development and startup support"
    ]
    
    for text in industry_tests:
        industry = scraper.determine_industry_focus(text)
        logger.info(f"  📝 '{text}'")
        logger.info(f"     🎯 Industry: {industry}")
        logger.info("")
    
    # Test email extraction
    logger.info("\n📧 Email Extraction Tests:")
    email_tests = [
        "Contact funding@screenaustralia.gov.au for more information",
        "Apply through grants@creative.gov.au by the deadline",
        "Questions? Email support@create.nsw.gov.au",
        "No email provided in this grant description"
    ]
    
    for text in email_tests:
        email = scraper.extract_email(text)
        logger.info(f"  📝 '{text}'")
        logger.info(f"     📧 Email: {email or 'Not found'}")
        logger.info("")
    
    # Test organization type extraction
    logger.info("\n🏢 Organization Type Detection:")
    org_tests = [
        "Available to individuals, small businesses, and not for profit organizations",
        "Open to startups and social enterprises in the creative sector",
        "Suitable for corporations and educational institutions",
        "Individuals and freelance artists may apply"
    ]
    
    for text in org_tests:
        org_types = scraper.extract_org_types(text)
        logger.info(f"  📝 '{text}'")
        logger.info(f"     🏢 Types: {', '.join(org_types)}")
        logger.info("")

def demo_scraper_sources():
    """Demonstrate the scraper source configuration."""
    logger.info("\n🌐 Australian Grants Scraper - Target Sources")
    logger.info("=" * 60)
    
    scraper = AustralianGrantsScraperDemo()
    
    for source_name, config in scraper.sources.items():
        logger.info(f"\n📌 {source_name.upper()}")
        logger.info(f"   🌍 URL: {config['base_url']}")
        logger.info(f"   📋 Description: {config['description']}")
        logger.info(f"   🔗 Endpoints ({len(config['endpoints'])}):")
        for endpoint in config['endpoints']:
            logger.info(f"      • {endpoint}")

def demo_sample_grants():
    """Show what kind of grants the scraper would find."""
    logger.info("\n🎁 Sample Grants the Scraper Would Find")
    logger.info("=" * 60)
    
    sample_grants = [
        {
            "title": "Screen Australia Documentary Production",
            "description": "Funding for documentary production by Australian practitioners. Supports creative development, production and post-production of documentaries with cultural and commercial appeal.",
            "source": "Screen Australia",
            "amount_min": 50000,
            "amount_max": 500000,
            "deadline": "2024-12-31",
            "industry_focus": "media",
            "org_types": ["individual", "small_business"],
            "contact_email": "funding@screenaustralia.gov.au"
        },
        {
            "title": "Creative Australia Arts Projects for Organisations",
            "description": "Support for arts organisations to deliver projects that benefit the arts sector and wider public, including national and international audiences.",
            "source": "Creative Australia", 
            "amount_min": 10000,
            "amount_max": 50000,
            "deadline": "2025-09-02",
            "industry_focus": "creative_arts",
            "org_types": ["not_for_profit", "small_business"],
            "contact_email": "arts@creative.gov.au"
        },
        {
            "title": "NSW Quick Response Funding",
            "description": "Fast-track funding for time-sensitive creative projects and opportunities that align with NSW cultural priorities.",
            "source": "Create NSW",
            "amount_min": 5000,
            "amount_max": 25000,
            "deadline": "2024-06-30",
            "industry_focus": "creative_arts",
            "org_types": ["any"],
            "contact_email": "quickresponse@create.nsw.gov.au"
        },
        {
            "title": "Business Development for Creative Industries",
            "description": "Support for creative businesses to develop new products, services, and market opportunities in the growing creative economy.",
            "source": "Business.gov.au",
            "amount_min": 15000,
            "amount_max": 100000,
            "deadline": "2024-08-15", 
            "industry_focus": "digital",
            "org_types": ["small_business", "startup"],
            "contact_email": "business@industry.gov.au"
        }
    ]
    
    for i, grant in enumerate(sample_grants, 1):
        logger.info(f"\n🎁 Grant {i}: {grant['title']}")
        logger.info(f"   🏛️  Source: {grant['source']}")
        logger.info(f"   📝 Description: {grant['description'][:100]}...")
        logger.info(f"   💰 Amount: ${grant['amount_min']:,} - ${grant['amount_max']:,}")
        logger.info(f"   📅 Deadline: {grant['deadline']}")
        logger.info(f"   🎯 Industry: {grant['industry_focus']}")
        logger.info(f"   🏢 Eligible: {', '.join(grant['org_types'])}")
        logger.info(f"   📧 Contact: {grant['contact_email']}")

def demo_benefits():
    """Show the benefits of the new scraper."""
    logger.info("\n✨ Benefits for Shadow Goose Entertainment")
    logger.info("=" * 60)
    
    benefits = [
        ("🎯 Industry-Specific", "Targets media, screen, and creative industry funding"),
        ("🌐 Multi-Source", "4+ reliable Australian government sources"),
        ("🔄 Reliable", "If one source fails, others continue working"),
        ("🤖 Intelligent", "Automatically extracts amounts, dates, eligibility"),
        ("📊 Structured", "Consistent data format across all sources"),
        ("🛡️ Robust", "Comprehensive error handling and logging"),
        ("⚡ Fast", "Parallel processing with respectful rate limiting"),
        ("🔧 Maintainable", "Well-documented and tested codebase")
    ]
    
    for icon_title, description in benefits:
        logger.info(f"   {icon_title}: {description}")

def main():
    """Run the full demonstration."""
    logger.info("🚀 Australian Grants Scraper - Live Demonstration")
    logger.info("🇦🇺 Specifically designed for Australian creative industries")
    logger.info("🎬 Perfect for Shadow Goose Entertainment")
    logger.info("")
    
    # Show scraper configuration
    demo_scraper_sources()
    
    # Demonstrate data extraction
    demo_data_extraction()
    
    # Show sample grants
    demo_sample_grants()
    
    # Show benefits
    demo_benefits()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ Demonstration Complete!")
    logger.info("🎯 The scraper is ready to replace the problematic GrantConnect scraper")
    logger.info("📊 It will provide comprehensive, reliable Australian grant data")
    logger.info("🚀 Perfect for finding relevant funding opportunities!")

if __name__ == "__main__":
    main()