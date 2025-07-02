import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.grant import Grant

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
        # TODO: Implement actual scraping logic
        logger.info("Running Business.gov.au scraper")
        return []

class GrantConnectScraper(BaseScraper):
    async def scrape(self) -> List[dict]:
        # TODO: Implement actual scraping logic
        logger.info("Running GrantConnect scraper")
        return []

class CommunityGrantsScraper(BaseScraper):
    async def scrape(self) -> List[dict]:
        # TODO: Implement actual scraping logic
        logger.info("Running Community Grants scraper")
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