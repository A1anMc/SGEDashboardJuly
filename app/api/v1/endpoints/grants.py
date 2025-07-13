from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.grant import Grant
from app.schemas.grant import GrantResponse, GrantList
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

@router.get("/", response_model=GrantList)
def get_grants(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    source: Optional[str] = None,
    industry_focus: Optional[str] = Query(None, enum=INDUSTRY_FOCUS_OPTIONS),
    location: Optional[str] = Query(None, enum=LOCATION_ELIGIBILITY_OPTIONS),
    org_type: Optional[str] = Query(None, enum=ORG_TYPE_OPTIONS),
    status: Optional[str] = Query(None, enum=["open", "closed", "draft", "active"])
):
    """Get list of grants with optional filtering."""
    try:
        query = db.query(Grant)
        
        if source:
            query = query.filter(Grant.source == source)
        
        if industry_focus:
            query = query.filter(Grant.industry_focus == industry_focus)
            
        if location:
            query = query.filter(Grant.location_eligibility == location)
            
        if org_type:
            query = query.filter(Grant.org_type_eligible.contains([org_type]))
            
        if status:
            query = query.filter(Grant.status == status)
        
        total = query.count()
        grants = query.offset(skip).limit(limit).all()
        
        # Calculate pagination
        page = skip // limit + 1
        has_next = skip + limit < total
        has_prev = page > 1
        
        return GrantList(
            items=grants,
            total=total,
            page=page,
            size=limit,
            has_next=has_next,
            has_prev=has_prev
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching grants: {str(e)}"
        )

@router.post("/scrape")
async def scrape_all_sources(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger scraping of all available grant sources."""
    try:
        scraper_service = ScraperService(db)
        
        # Start scraping in the background
        background_tasks.add_task(scraper_service.scrape_all)
        
        return {
            "status": "started",
            "message": "Grant scraping has been initiated",
            "available_sources": scraper_service.get_available_sources()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start scraper: {str(e)}"
        )

@router.post("/scrape/{source}")
async def scrape_specific_source(
    source: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger scraping of a specific grant source."""
    try:
        scraper_service = ScraperService(db)
        
        # Validate source
        available_sources = scraper_service.get_available_sources()
        if source not in available_sources:
            raise HTTPException(
                status_code=404,
                detail=f"Source '{source}' not found. Available sources: {available_sources}"
            )
        
        # Start scraping in the background
        background_tasks.add_task(scraper_service.scrape_source, source)
        
        return {
            "status": "started",
            "message": f"Scraping initiated for source: {source}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start scraper for {source}: {str(e)}"
        )

@router.get("/sources")
def get_available_sources(db: Session = Depends(get_db)):
    """Get list of available grant sources with their status."""
    try:
        scraper_service = ScraperService(db)
        sources = scraper_service.get_available_sources()
        
        return {
            "sources": sources,
            "total": len(sources),
            "status": "active"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching sources: {str(e)}"
        ) 