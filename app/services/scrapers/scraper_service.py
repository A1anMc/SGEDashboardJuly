import logging
import asyncio
from typing import Dict, List, Type
from sqlalchemy.orm import Session

from app.models.scraper_log import ScraperLog
from app.services.scrapers.base_scraper import BaseScraper
from app.services.scrapers.business_gov import BusinessGovScraper
from app.services.scrapers.grantconnect import GrantConnectScraper
from app.services.scrapers.dummy_scraper import DummyScraper
from app.services.scrapers.australian_grants_scraper import AustralianGrantsScraper
from app.services.scrapers.current_grants_scraper import CurrentGrantsScraper
from app.services.scrapers.philanthropic_scraper import PhilanthropicScraper
from app.services.scrapers.council_scraper import CouncilScraper
from app.services.scrapers.media_investment_scraper import MediaInvestmentScraper

logger = logging.getLogger(__name__)

class ScraperService:
    """Service for managing and executing grant scrapers."""
    
    def __init__(self, db: Session):
        self.db = db
        self.scrapers: Dict[str, Type[BaseScraper]] = {
            "business.gov.au": BusinessGovScraper,
            "grantconnect": GrantConnectScraper,
            "dummy": DummyScraper,
            "australian_grants": AustralianGrantsScraper,
            "current_grants": CurrentGrantsScraper,
            "philanthropic": PhilanthropicScraper,
            "councils": CouncilScraper,
            "media_investment": MediaInvestmentScraper
        }
    
    def get_available_sources(self) -> List[str]:
        """Get list of available scraper sources."""
        return list(self.scrapers.keys())
    
    async def scrape_source(self, source_name: str) -> Dict:
        """Scrape grants from a specific source with logging."""
        if source_name not in self.scrapers:
            raise ValueError(f"Unknown source: {source_name}")
        
        # Create log entry
        log = ScraperLog(source_name=source_name, status="running")
        self.db.add(log)
        self.db.commit()
        
        try:
            # Initialize and run scraper
            scraper = self.scrapers[source_name](self.db)
            
            # Handle both sync and async scrapers
            if asyncio.iscoroutinefunction(scraper.scrape):
                grants_found = await scraper.scrape()
            else:
                grants_found = scraper.scrape()
            
            # Count new and updated grants
            grants_added = len([g for g in grants_found if not g.id])
            grants_updated = len(grants_found) - grants_added
            
            # Update log with success
            log.complete(
                status="success",
                grants_found=len(grants_found),
                grants_added=grants_added,
                grants_updated=grants_updated,
                metadata={
                    "urls_scraped": scraper.urls_scraped if hasattr(scraper, 'urls_scraped') else None,
                    "rate_limits": scraper.rate_limits if hasattr(scraper, 'rate_limits') else None
                }
            )
            
            return {
                "status": "success",
                "grants_found": len(grants_found),
                "grants_added": grants_added,
                "grants_updated": grants_updated,
                "duration_seconds": log.duration_seconds
            }
            
        except Exception as e:
            # Update log with error
            log.complete(
                status="error",
                error_message=str(e)
            )
            raise
        
        finally:
            self.db.commit()
    
    async def scrape_all(self) -> Dict[str, Dict]:
        """Scrape all available sources."""
        results = {}
        for source in self.get_available_sources():
            try:
                results[source] = await self.scrape_source(source)
            except Exception as e:
                results[source] = {
                    "status": "error",
                    "error": str(e)
                }
        return results

async def scrape_community_grants(self) -> List[Dict]:
    """
    Scrape grants from community sources.
    """
    grants = []
    
    try:
        # TODO: Add specific community grant sources
        pass
    except Exception as e:
        logger.error(f"Error scraping community grants: {str(e)}")
    
    return grants 