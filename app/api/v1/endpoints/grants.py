from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.grant import Grant
from app.schemas.grant import GrantResponse
from app.services.scrapers.scraper_service import ScraperService

router = APIRouter()

# Industry focus options
INDUSTRY_FOCUS_OPTIONS = [
    "technology", "healthcare", "education", "environment",
    "agriculture", "manufacturing", "services", "research", "other"
]

# Location eligibility options
LOCATION_ELIGIBILITY_OPTIONS = [
    "national", "state", "regional", "local", "international"
]

# Organization type options
ORG_TYPE_OPTIONS = [
    "startup", "sme", "enterprise", "nonprofit", "government", "academic", "any"
]

@router.get("/", response_model=List[GrantResponse])
def get_grants(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    source: Optional[str] = None,
    industry_focus: Optional[str] = Query(None, enum=INDUSTRY_FOCUS_OPTIONS),
    location: Optional[str] = Query(None, enum=LOCATION_ELIGIBILITY_OPTIONS),
    org_type: Optional[str] = Query(None, enum=ORG_TYPE_OPTIONS)
):
    """Get list of grants with optional filtering."""
    query = db.query(Grant)
    
    if source:
        query = query.filter(Grant.source == source)
    
    if industry_focus:
        query = query.filter(Grant.industry_focus == industry_focus)
        
    if location:
        query = query.filter(Grant.location_eligibility == location)
        
    if org_type:
        query = query.filter(Grant.org_type_eligible.contains([org_type]))
    
    return query.offset(skip).limit(limit).all()

@router.post("/scrape")
def scrape_all_sources(db: Session = Depends(get_db)):
    """Trigger scraping of all available grant sources."""
    try:
        scraper_service = ScraperService(db)
        results = scraper_service.scrape_all()
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape/{source}")
def scrape_specific_source(source: str, db: Session = Depends(get_db)):
    """Trigger scraping of a specific grant source."""
    try:
        scraper_service = ScraperService(db)
        result = scraper_service.scrape_source(source)
        return {
            "status": "success",
            "result": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources")
def get_available_sources(db: Session = Depends(get_db)):
    """Get list of available grant sources."""
    scraper_service = ScraperService(db)
    return {
        "sources": scraper_service.get_available_sources()
    } 