#!/usr/bin/env python3
"""
Test script for the Australian Grants Scraper

This script demonstrates how to use the new Australian grants scraper
and provides a way to test it manually.

Usage:
    python scripts/test_australian_scraper.py
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.scrapers.australian_grants_scraper import AustralianGrantsScraper
from unittest.mock import Mock
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def setup_mock_db():
    """Set up a mock database session for testing."""
    return Mock(spec=Session)

async def test_scraper():
    """Test the Australian grants scraper."""
    logger.info("Starting Australian Grants Scraper test")
    
    # Set up mock database
    db_session = setup_mock_db()
    
    # Create scraper instance
    scraper = AustralianGrantsScraper(db_session)
    
    logger.info(f"Configured scraper with {len(scraper.sources)} sources:")
    for source_name, config in scraper.sources.items():
        logger.info(f"  - {source_name}: {config['description']}")
        logger.info(f"    Base URL: {config['base_url']}")
        logger.info(f"    Endpoints: {len(config['endpoints'])}")
    
    try:
        # Test the scraper
        start_time = datetime.now()
        logger.info("Starting scraping process...")
        
        grants = await scraper.scrape()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"Scraping completed in {duration:.2f} seconds")
        logger.info(f"Total grants found: {len(grants)}")
        
        # Display results
        if grants:
            logger.info("\nGrant Summary:")
            
            # Group by source
            by_source = {}
            for grant in grants:
                source = grant.get('source', 'Unknown')
                if source not in by_source:
                    by_source[source] = []
                by_source[source].append(grant)
            
            for source, source_grants in by_source.items():
                logger.info(f"\n{source}: {len(source_grants)} grants")
                
                for i, grant in enumerate(source_grants[:3], 1):  # Show first 3 grants per source
                    logger.info(f"  {i}. {grant.get('title', 'No title')[:60]}...")
                    if grant.get('amount_max'):
                        logger.info(f"     Amount: Up to ${grant['amount_max']:,}")
                    if grant.get('deadline'):
                        logger.info(f"     Deadline: {grant['deadline']}")
                    if grant.get('industry_focus'):
                        logger.info(f"     Industry: {grant['industry_focus']}")
                
                if len(source_grants) > 3:
                    logger.info(f"     ... and {len(source_grants) - 3} more grants")
        
        else:
            logger.warning("No grants were found. This might indicate:")
            logger.warning("- Network connectivity issues")
            logger.warning("- Website structure changes")
            logger.warning("- Rate limiting or blocking")
            logger.warning("- Parsing logic needs updates")
        
        return grants
        
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        return []

async def test_individual_source(source_name: str):
    """Test scraping from a single source."""
    logger.info(f"Testing individual source: {source_name}")
    
    db_session = setup_mock_db()
    scraper = AustralianGrantsScraper(db_session)
    
    if source_name not in scraper.sources:
        logger.error(f"Unknown source: {source_name}")
        logger.info(f"Available sources: {list(scraper.sources.keys())}")
        return []
    
    try:
        source_config = scraper.sources[source_name]
        
        # Create a session for the scraper
        import aiohttp
        async with aiohttp.ClientSession(
            headers=scraper.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            scraper.session = session
            grants = await scraper._scrape_source(source_name, source_config)
        
        logger.info(f"Found {len(grants)} grants from {source_name}")
        
        # Show detailed results
        for i, grant in enumerate(grants[:5], 1):
            logger.info(f"\nGrant {i}:")
            logger.info(f"  Title: {grant.get('title', 'No title')}")
            logger.info(f"  Description: {grant.get('description', 'No description')[:100]}...")
            logger.info(f"  URL: {grant.get('source_url', 'No URL')}")
            if grant.get('amount_max'):
                logger.info(f"  Max Amount: ${grant['amount_max']:,}")
            if grant.get('deadline'):
                logger.info(f"  Deadline: {grant['deadline']}")
        
        return grants
        
    except Exception as e:
        logger.error(f"Error testing {source_name}: {str(e)}")
        return []

def test_data_extraction():
    """Test data extraction methods."""
    logger.info("Testing data extraction methods")
    
    db_session = setup_mock_db()
    scraper = AustralianGrantsScraper(db_session)
    
    # Test amount extraction
    test_texts = [
        "Funding up to $50,000 is available",
        "Between $10,000 and $100,000",
        "Maximum funding of $1,500,000",
        "Grants range from $5,000 to $50,000"
    ]
    
    logger.info("\nTesting amount extraction:")
    for text in test_texts:
        min_amt, max_amt = scraper._extract_amounts(text)
        logger.info(f"  '{text}' -> Min: {min_amt}, Max: {max_amt}")
    
    # Test date extraction
    date_texts = [
        "Applications close on 31 December 2024",
        "Deadline: 15/03/2025",
        "Opens 1 January 2024, closes 31 March 2024"
    ]
    
    logger.info("\nTesting date extraction:")
    for text in date_texts:
        dates = scraper._extract_dates(text)
        logger.info(f"  '{text}' -> Open: {dates['open_date']}, Close: {dates['deadline']}")
    
    # Test industry focus
    industry_texts = [
        "Film and television production funding",
        "Support for creative artists and performers",
        "Digital technology innovation grants",
        "General business development support"
    ]
    
    logger.info("\nTesting industry focus detection:")
    for text in industry_texts:
        industry = scraper._determine_industry_focus(text)
        logger.info(f"  '{text}' -> {industry}")

async def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "test-source" and len(sys.argv) > 2:
            source_name = sys.argv[2]
            await test_individual_source(source_name)
        elif command == "test-extraction":
            test_data_extraction()
        elif command == "help":
            print("Usage:")
            print("  python scripts/test_australian_scraper.py                  # Run full test")
            print("  python scripts/test_australian_scraper.py test-source screen_australia  # Test specific source")
            print("  python scripts/test_australian_scraper.py test-extraction # Test data extraction")
            print("  python scripts/test_australian_scraper.py help            # Show this help")
        else:
            logger.error(f"Unknown command: {command}")
            print("Use 'help' for usage information")
    else:
        # Run full test
        grants = await test_scraper()
        
        # Also test data extraction
        logger.info("\n" + "="*50)
        test_data_extraction()
        
        logger.info(f"\nTest completed. Total grants found: {len(grants)}")

if __name__ == "__main__":
    # Set up event loop and run
    if sys.platform.startswith('win'):
        # Windows specific event loop policy
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())