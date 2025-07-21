from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models.grant import Grant
from app.schemas.grant import GrantResponse, GrantList
# from app.services.scrapers.scraper_service import ScraperService  # Disabled - requires bs4

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
        # Use direct engine access instead of dependency injection
        from app.db.session import get_engine
        from sqlalchemy import text
        
        engine = get_engine()
        with engine.connect() as conn:
            # Simple query to get grants count
            result = conn.execute(text("SELECT COUNT(*) FROM grants"))
            total = result.scalar()
            
            # For now, return empty list since we're testing the connection
            # TODO: Implement full query logic once connection is confirmed working
            
        return GrantList(
            items=[],
            total=total,
            page=skip // limit + 1,
            size=limit,
            has_next=skip + limit < total,
            has_prev=skip > 0
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
    return {
        "status": "disabled",
        "message": "Grant scraping is currently disabled to reduce dependencies",
        "available_sources": []
    }

@router.post("/scrape/{source}")
async def scrape_specific_source(
    source: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger scraping of a specific grant source."""
    return {
        "status": "disabled",
        "message": f"Grant scraping for {source} is currently disabled to reduce dependencies"
    }

@router.get("/sources")
def get_available_sources(db: Session = Depends(get_db)):
    """Get list of available grant sources with their status."""
    return {
        "sources": [],
        "total": 0,
        "status": "disabled",
        "message": "Grant scraping sources are currently disabled to reduce dependencies"
    }

@router.get("/test")
def test_grants():
    """Test endpoint that doesn't use dependency injection."""
    try:
        from app.db.session import get_engine
        from sqlalchemy import text
        
        engine = get_engine()
        with engine.connect() as conn:
            # Check if grants table exists
            result = conn.execute(text("SELECT COUNT(*) FROM grants"))
            count = result.scalar()
            
        return {
            "status": "success",
            "grants_count": count,
            "message": "Direct database access working"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Direct database access failed"
        } 