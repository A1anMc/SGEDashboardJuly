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
        # Use direct engine access with SQLAlchemy ORM
        from app.db.session import get_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.grant import Grant
        from sqlalchemy import and_, or_
        
        engine = get_engine()
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Build query with filters
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
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            grants = query.offset(skip).limit(limit).all()
            
            # Convert to response format
            grant_items = []
            for grant in grants:
                grant_items.append({
                    "id": grant.id,
                    "title": grant.title,
                    "description": grant.description,
                    "source": grant.source,
                    "source_url": grant.source_url,
                    "application_url": grant.application_url,
                    "contact_email": grant.contact_email,
                    "min_amount": float(grant.min_amount) if grant.min_amount else None,
                    "max_amount": float(grant.max_amount) if grant.max_amount else None,
                    "open_date": grant.open_date.isoformat() if grant.open_date else None,
                    "deadline": grant.deadline.isoformat() if grant.deadline else None,
                    "industry_focus": grant.industry_focus,
                    "location_eligibility": grant.location_eligibility,
                    "org_type_eligible": grant.org_type_eligible or [],
                    "funding_purpose": grant.funding_purpose or [],
                    "audience_tags": grant.audience_tags or [],
                    "status": grant.status,
                    "notes": grant.notes,
                    "created_at": grant.created_at.isoformat() if grant.created_at else None,
                    "updated_at": grant.updated_at.isoformat() if grant.updated_at else None
                })
            
            return GrantList(
                items=grant_items,
                total=total,
                page=skip // limit + 1,
                size=limit,
                has_next=skip + limit < total,
                has_prev=skip > 0
            )
            
        finally:
            db.close()
            
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

@router.post("/add-test")
def add_test_grant():
    """Add a single test grant to the database."""
    try:
        from app.db.session import get_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.grant import Grant
        from datetime import datetime, timedelta
        
        engine = get_engine()
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Create a simple test grant
            test_grant = Grant(
                title="Test Community Grant",
                description="A test grant for community development",
                source="Test Foundation",
                source_url="https://example.com/test",
                application_url="https://example.com/apply",
                contact_email="test@example.com",
                min_amount=1000.00,
                max_amount=10000.00,
                open_date=datetime.now(),
                deadline=datetime.now() + timedelta(days=30),
                industry_focus="community",
                location_eligibility="local",
                org_type_eligible=["nonprofit"],
                funding_purpose=["community development"],
                audience_tags=["community organizations"],
                status="open"
            )
            
            db.add(test_grant)
            db.commit()
            
            return {
                "status": "success",
                "message": "Added test grant",
                "grant_id": test_grant.id
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to add test grant"
        }

@router.post("/seed")
def seed_sample_grants():
    """Add sample grants to the database for testing."""
    try:
        from app.db.session import get_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.grant import Grant
        from datetime import datetime, timedelta
        
        engine = get_engine()
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            # Check if grants already exist
            existing_count = db.query(Grant).count()
            if existing_count > 0:
                return {
                    "status": "info",
                    "message": f"Database already has {existing_count} grants",
                    "grants_count": existing_count
                }
            
            # Sample grants data
            sample_grants = [
                {
                    "title": "Community Innovation Grant",
                    "description": "Supporting innovative community projects that address local challenges",
                    "source": "Community Foundation",
                    "source_url": "https://example.com/community-grant",
                    "application_url": "https://example.com/apply",
                    "contact_email": "grants@communityfoundation.org",
                    "min_amount": 5000.00,
                    "max_amount": 25000.00,
                    "open_date": datetime.now(),
                    "deadline": datetime.now() + timedelta(days=30),
                    "industry_focus": "community",
                    "location_eligibility": "local",
                    "org_type_eligible": ["nonprofit", "community"],
                    "funding_purpose": ["innovation", "community development"],
                    "audience_tags": ["local communities", "innovation"],
                    "status": "open"
                },
                {
                    "title": "Technology for Social Impact",
                    "description": "Grants for technology solutions that create positive social impact",
                    "source": "Tech for Good Foundation",
                    "source_url": "https://example.com/tech-grant",
                    "application_url": "https://example.com/tech-apply",
                    "contact_email": "tech@techforgood.org",
                    "min_amount": 10000.00,
                    "max_amount": 50000.00,
                    "open_date": datetime.now() - timedelta(days=10),
                    "deadline": datetime.now() + timedelta(days=45),
                    "industry_focus": "technology",
                    "location_eligibility": "national",
                    "org_type_eligible": ["startup", "nonprofit", "academic"],
                    "funding_purpose": ["technology", "social impact"],
                    "audience_tags": ["tech startups", "social enterprises"],
                    "status": "open"
                },
                {
                    "title": "Environmental Sustainability Fund",
                    "description": "Supporting projects that promote environmental sustainability",
                    "source": "Green Future Initiative",
                    "source_url": "https://example.com/environmental-grant",
                    "application_url": "https://example.com/env-apply",
                    "contact_email": "environment@greenfuture.org",
                    "min_amount": 15000.00,
                    "max_amount": 75000.00,
                    "open_date": datetime.now() - timedelta(days=5),
                    "deadline": datetime.now() + timedelta(days=60),
                    "industry_focus": "environment",
                    "location_eligibility": "regional",
                    "org_type_eligible": ["nonprofit", "academic", "government"],
                    "funding_purpose": ["environmental", "sustainability"],
                    "audience_tags": ["environmental organizations", "sustainability"],
                    "status": "open"
                }
            ]
            
            # Add grants to database
            for grant_data in sample_grants:
                grant = Grant(**grant_data)
                db.add(grant)
            
            db.commit()
            
            return {
                "status": "success",
                "message": f"Added {len(sample_grants)} sample grants",
                "grants_count": len(sample_grants)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to seed sample grants"
        } 