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

@router.post("/clear")
def clear_all_grants():
    """Clear all grants from the database."""
    db = next(get_db())
    
    try:
        # Delete all grants
        deleted_count = db.query(Grant).delete()
        db.commit()
        
        return {
            "message": f"Successfully cleared {deleted_count} grants from the database",
            "grants_deleted": deleted_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing grants: {str(e)}")
    finally:
        db.close()

@router.post("/seed-simple")
def seed_simple_grants():
    """Seed the database with a simple set of diverse grants for testing."""
    db = next(get_db())
    
    # Check if grants already exist
    existing_count = db.query(Grant).count()
    if existing_count > 0:
        return {
            "message": f"Database already has {existing_count} grants. Use /clear first to reset.",
            "existing_grants": existing_count
        }
    
    sample_grants = [
        # MEDIA SECTOR
        {
            "title": "Digital Media Innovation Fund",
            "description": "Supporting innovative digital media projects that push creative boundaries and engage new audiences through technology.",
            "source": "Creative Australia",
            "source_url": "https://creative.gov.au",
            "application_url": "https://creative.gov.au/apply",
            "contact_email": "grants@creative.gov.au",
            "min_amount": 50000,
            "max_amount": 200000,
            "open_date": datetime.now(),
            "deadline": datetime.now() + timedelta(days=45),
            "industry_focus": "technology",
            "location_eligibility": "National",
            "org_type_eligible": ["Startup", "SME", "Nonprofit"],
            "funding_purpose": ["Digital Media", "Innovation"],
            "audience_tags": ["Digital Creators", "Tech Startups"],
            "status": "open",
            "notes": "Focus on digital storytelling"
        },
        {
            "title": "Indigenous Film Production Grant",
            "description": "Supporting Indigenous filmmakers to tell authentic stories and preserve cultural heritage through film.",
            "source": "Screen Australia",
            "source_url": "https://screenaustralia.gov.au",
            "application_url": "https://screenaustralia.gov.au/indigenous",
            "contact_email": "indigenous@screenaustralia.gov.au",
            "min_amount": 25000,
            "max_amount": 150000,
            "open_date": datetime.now(),
            "deadline": datetime.now() + timedelta(days=30),
            "industry_focus": "services",
            "location_eligibility": "National",
            "org_type_eligible": ["Indigenous Business", "Nonprofit"],
            "funding_purpose": ["Film Production", "Cultural Preservation"],
            "audience_tags": ["Indigenous Communities", "Filmmakers"],
            "status": "open",
            "notes": "Priority for Indigenous-owned companies"
        },
        
        # COMMUNITY SECTOR
        {
            "title": "Youth Mental Health Initiative",
            "description": "Supporting community organizations to provide mental health services and support programs for young people.",
            "source": "Department of Health",
            "source_url": "https://health.gov.au",
            "application_url": "https://health.gov.au/youth-mental-health",
            "contact_email": "youth.health@health.gov.au",
            "min_amount": 50000,
            "max_amount": 500000,
            "open_date": datetime.now(),
            "deadline": datetime.now() + timedelta(days=75),
            "industry_focus": "healthcare",
            "location_eligibility": "National",
            "org_type_eligible": ["Nonprofit", "Healthcare Provider"],
            "funding_purpose": ["Mental Health", "Youth Services"],
            "audience_tags": ["Youth", "Mental Health Professionals"],
            "status": "open",
            "notes": "Priority for evidence-based programs"
        },
        {
            "title": "Social Enterprise Accelerator",
            "description": "Supporting social enterprises to scale their impact and create sustainable business models.",
            "source": "Social Traders",
            "source_url": "https://socialtraders.com.au",
            "application_url": "https://socialtraders.com.au/accelerator",
            "contact_email": "accelerator@socialtraders.com.au",
            "min_amount": 25000,
            "max_amount": 150000,
            "open_date": datetime.now(),
            "deadline": datetime.now() + timedelta(days=30),
            "industry_focus": "services",
            "location_eligibility": "National",
            "org_type_eligible": ["Social Enterprise", "Nonprofit"],
            "funding_purpose": ["Social Enterprise", "Business Development"],
            "audience_tags": ["Social Entrepreneurs", "Nonprofits"],
            "status": "open",
            "notes": "Must have proven social impact model"
        },
        
        # SUSTAINABILITY SECTOR
        {
            "title": "Renewable Energy Innovation Grant",
            "description": "Supporting innovative renewable energy projects that can accelerate Australia's transition to clean energy.",
            "source": "Australian Renewable Energy Agency",
            "source_url": "https://arena.gov.au",
            "application_url": "https://arena.gov.au/innovation",
            "contact_email": "innovation@arena.gov.au",
            "min_amount": 100000,
            "max_amount": 2000000,
            "open_date": datetime.now(),
            "deadline": datetime.now() + timedelta(days=120),
            "industry_focus": "technology",
            "location_eligibility": "National",
            "org_type_eligible": ["Startup", "SME", "Research Institution"],
            "funding_purpose": ["Renewable Energy", "Innovation"],
            "audience_tags": ["Energy Companies", "Researchers"],
            "status": "open",
            "notes": "Must demonstrate commercial potential"
        },
        {
            "title": "Circular Economy Solutions",
            "description": "Supporting businesses to develop circular economy solutions that reduce waste and create sustainable value chains.",
            "source": "Circular Economy Australia",
            "source_url": "https://circulareconomy.org.au",
            "application_url": "https://circulareconomy.org.au/solutions-fund",
            "contact_email": "solutions@circulareconomy.org.au",
            "min_amount": 25000,
            "max_amount": 300000,
            "open_date": datetime.now(),
            "deadline": datetime.now() + timedelta(days=75),
            "industry_focus": "manufacturing",
            "location_eligibility": "National",
            "org_type_eligible": ["Startup", "SME", "Nonprofit"],
            "funding_purpose": ["Circular Economy", "Waste Reduction"],
            "audience_tags": ["Manufacturers", "Sustainability Experts"],
            "status": "open",
            "notes": "Focus on scalable circular economy models"
        },
        {
            "title": "Sustainable Agriculture Innovation",
            "description": "Supporting farmers to adopt sustainable practices and reduce environmental impact.",
            "source": "Department of Agriculture",
            "source_url": "https://agriculture.gov.au",
            "application_url": "https://agriculture.gov.au/sustainable-ag",
            "contact_email": "sustainable.ag@agriculture.gov.au",
            "min_amount": 50000,
            "max_amount": 500000,
            "open_date": datetime.now(),
            "deadline": datetime.now() + timedelta(days=90),
            "industry_focus": "agriculture",
            "location_eligibility": "Regional",
            "org_type_eligible": ["SME", "Farmer", "Research Institution"],
            "funding_purpose": ["Sustainable Agriculture", "Innovation"],
            "audience_tags": ["Farmers", "Agricultural Researchers"],
            "status": "active",
            "notes": "Must demonstrate environmental benefits"
        },
        {
            "title": "Marine Conservation Initiative",
            "description": "Supporting marine conservation projects that protect Australia's unique marine ecosystems.",
            "source": "Great Barrier Reef Foundation",
            "source_url": "https://barrierreef.org",
            "application_url": "https://barrierreef.org/conservation",
            "contact_email": "conservation@barrierreef.org",
            "min_amount": 25000,
            "max_amount": 250000,
            "open_date": datetime.now(),
            "deadline": datetime.now() + timedelta(days=45),
            "industry_focus": "environment",
            "location_eligibility": "Coastal",
            "org_type_eligible": ["Nonprofit", "Research Institution"],
            "funding_purpose": ["Marine Conservation", "Biodiversity"],
            "audience_tags": ["Marine Biologists", "Conservationists"],
            "status": "open",
            "notes": "Priority for Great Barrier Reef projects"
        }
    ]
    
    try:
        for grant_data in sample_grants:
            grant = Grant(**grant_data)
            db.add(grant)
        
        db.commit()
        return {
            "message": f"Successfully seeded {len(sample_grants)} diverse grants across Media, Community Impact, and Sustainability sectors",
            "grants_added": len(sample_grants),
            "sectors": ["Media & Creative", "Community & Social Impact", "Sustainability & Environment"],
            "note": "Simple test dataset with 8 grants for comprehensive testing"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error seeding grants: {str(e)}")
    finally:
        db.close() 