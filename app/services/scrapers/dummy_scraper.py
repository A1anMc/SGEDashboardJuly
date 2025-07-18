from typing import List, Dict, Any
from datetime import datetime, timedelta
import random
import time
from sqlalchemy.orm import Session

from app.services.scrapers.base_scraper import BaseScraper
from app.models.grant import Grant

class DummyScraper(BaseScraper):
    """Dummy scraper for testing and development."""
    
    def __init__(self, db: Session):
        super().__init__(db, "dummy")
        self.urls_scraped = []
    
    async def scrape(self) -> List[Grant]:
        """Generate dummy grant data for testing."""
        grants_data = []
        num_grants = random.randint(3, 7)
        
        for i in range(num_grants):
            # Simulate network delay
            time.sleep(random.uniform(0.1, 0.5))
            
            # Generate random dates
            open_date = datetime.now() + timedelta(days=random.randint(1, 30))
            deadline = open_date + timedelta(days=random.randint(30, 90))
            
            # Create dummy grant data as dictionary
            grant_data = {
                "title": f"Test Grant {i + 1}",
                "description": f"This is a test grant generated by the dummy scraper (#{i + 1})",
                "source_url": f"https://example.com/grants/{i + 1}",
                "min_amount": random.randint(1000, 5000),
                "max_amount": random.randint(5000, 50000),
                "open_date": open_date,
                "deadline": deadline,
                "industry_focus": random.choice(["technology", "arts", "healthcare", "education"]),
                "location_eligibility": random.choice(["national", "state", "regional"]),
                "org_type_eligible": ["not_for_profit", "small_business"],
                "funding_purpose": ["development", "research"],
                "audience_tags": ["startup", "creative"],
                "status": "active"
            }
            
            # Add to list
            grants_data.append(grant_data)
            
            # Track URL for logging
            self.urls_scraped.append(grant_data["source_url"])
        
        # Save grants to database using BaseScraper method
        saved_grants = await self.save_grants(grants_data)
        
        return saved_grants 