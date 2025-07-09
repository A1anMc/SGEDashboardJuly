from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, timedelta
from app.core.deps import get_db, get_current_user
from app.models.grant import Grant
from app.models.user import User
from app.schemas.grant import (
    GrantCreate, GrantUpdate, GrantResponse, GrantList, GrantFilters,
    GrantMatchResult, ProjectProfile, GrantDashboard, GrantMetrics,
    GrantsByCategory, GrantTimeline, DeadlineGroup, MatchingInsights,
    ScraperRunRequest, ScraperRunResponse
)
from app.services.scrapers.business_gov import BusinessGovScraper
from app.services.scrapers.grantconnect import GrantConnectScraper
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Grant CRUD Operations
@router.post("/", response_model=GrantResponse)
async def create_grant(
    grant: GrantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new grant."""
    try:
        db_grant = Grant(**grant.dict())
        db.add(db_grant)
        db.commit()
        db.refresh(db_grant)
        logger.info(f"Created grant: {db_grant.title}")
        return db_grant
    except Exception as e:
        logger.error(f"Error creating grant: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=GrantList)
async def get_grants(
    filters: GrantFilters = Depends(),
    db: Session = Depends(get_db)
):
    """Get paginated list of grants with optional filtering."""
    try:
        query = db.query(Grant)
        
        # Apply filters
        if filters.industry_focus:
            query = query.filter(Grant.industry_focus == filters.industry_focus)
        if filters.location_eligibility:
            query = query.filter(Grant.location_eligibility == filters.location_eligibility)
        if filters.status:
            query = query.filter(Grant.status == filters.status)
        if filters.min_amount:
            query = query.filter(Grant.max_amount >= filters.min_amount)
        if filters.max_amount:
            query = query.filter(Grant.min_amount <= filters.max_amount)
        if filters.deadline_before:
            query = query.filter(Grant.deadline <= filters.deadline_before)
        if filters.deadline_after:
            query = query.filter(Grant.deadline >= filters.deadline_after)
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Grant.title.ilike(search_term),
                    Grant.description.ilike(search_term),
                    Grant.source.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (filters.page - 1) * filters.size
        grants = query.offset(offset).limit(filters.size).all()
        
        return GrantList(
            items=[GrantResponse.from_orm(grant) for grant in grants],
            total=total,
            page=filters.page,
            size=filters.size,
            has_next=offset + filters.size < total,
            has_prev=filters.page > 1
        )
    except Exception as e:
        logger.error(f"Error fetching grants: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching grants")

@router.get("/{grant_id}", response_model=GrantResponse)
async def get_grant(grant_id: int, db: Session = Depends(get_db)):
    """Get a specific grant by ID."""
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    return grant

@router.put("/{grant_id}", response_model=GrantResponse)
async def update_grant(
    grant_id: int,
    grant_update: GrantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing grant."""
    try:
        grant = db.query(Grant).filter(Grant.id == grant_id).first()
        if not grant:
            raise HTTPException(status_code=404, detail="Grant not found")
        
        # Update fields
        update_data = grant_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(grant, field, value)
        
        db.commit()
        db.refresh(grant)
        
        logger.info(f"Updated grant: {grant.title}")
        return grant
    except Exception as e:
        logger.error(f"Error updating grant {grant_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{grant_id}")
async def delete_grant(
    grant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a grant."""
    try:
        grant = db.query(Grant).filter(Grant.id == grant_id).first()
        if not grant:
            raise HTTPException(status_code=404, detail="Grant not found")
        
        db.delete(grant)
        db.commit()
        logger.info(f"Deleted grant: {grant.title}")
        return {"message": "Grant deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting grant {grant_id}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Grant Matching
@router.post("/match", response_model=List[GrantMatchResult])
async def match_grants(
    project_profile: ProjectProfile,
    min_score: int = Query(60, description="Minimum match score (0-100)"),
    limit: int = Query(10, description="Maximum number of matches to return"),
    db: Session = Depends(get_db)
):
    """Match grants against a project profile."""
    try:
        # Get all active grants
        grants = db.query(Grant).filter(Grant.status == "active").all()
        
        # Calculate match scores for all grants
        matches = []
        for grant in grants:
            match_result = grant.calculate_match_score(project_profile.dict())
            if match_result["score"] >= min_score:
                matches.append(GrantMatchResult(**match_result))
        
        # Sort by score descending and limit results
        matches.sort(key=lambda x: x.score, reverse=True)
        return matches[:limit]
    except Exception as e:
        logger.error(f"Error matching grants: {str(e)}")
        raise HTTPException(status_code=500, detail="Error matching grants")

@router.get("/{grant_id}/match-details", response_model=GrantMatchResult)
async def get_grant_match_details(
    grant_id: int,
    project_profile: ProjectProfile,
    db: Session = Depends(get_db)
):
    """Get detailed matching information for a specific grant."""
    try:
        grant = db.query(Grant).filter(Grant.id == grant_id).first()
        if not grant:
            raise HTTPException(status_code=404, detail="Grant not found")
        
        match_result = grant.calculate_match_score(project_profile.dict())
        return GrantMatchResult(**match_result)
    except Exception as e:
        logger.error(f"Error getting match details for grant {grant_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error getting match details")

# Dashboard
@router.get("/dashboard/data", response_model=GrantDashboard)
async def get_grant_dashboard(db: Session = Depends(get_db)):
    """Get comprehensive grant dashboard data."""
    try:
        # Get grant count
        grant_count = db.query(Grant).filter(Grant.status == "active").count()
        now = datetime.utcnow()
        
        # Mock data for now - will be replaced with real data once grants are populated
        metrics = GrantMetrics(
            total_active=grant_count,
            total_amount_available=5750000.0,
            upcoming_deadlines=12,
            avg_match_score=72.5
        )
        
        categories = GrantsByCategory(
            by_industry={
                "media": 20,
                "creative_arts": 15,
                "technology": 5,
                "general": 5
            },
            by_location={
                "VIC": 15,
                "NSW": 10,
                "Australia": 20
            },
            by_org_type={
                "social_enterprise": 25,
                "not_for_profit": 15,
                "small_medium_enterprise": 5
            },
            by_funding_range={
                "0-10k": 10,
                "10k-50k": 20,
                "50k-100k": 10,
                "100k+": 5
            }
        )
        
        # Mock timeline data
        timeline = GrantTimeline(
            this_week=DeadlineGroup(
                grants=[
                    {"id": 1, "title": "Arts Grant 2024", "deadline": (now + timedelta(days=3)).isoformat(), "amount": 50000}
                ],
                total_amount=150000.0,
                count=3
            ),
            next_week=DeadlineGroup(grants=[], total_amount=0.0, count=0),
            this_month=DeadlineGroup(grants=[], total_amount=250000.0, count=5),
            next_month=DeadlineGroup(grants=[], total_amount=500000.0, count=8),
            later=DeadlineGroup(grants=[], total_amount=1000000.0, count=15)
        )
        
        # Mock insights
        matching_insights = MatchingInsights(
            best_matches=[
                {"grant_id": 1, "title": "Screen Australia Fund", "score": 95},
                {"grant_id": 2, "title": "Creative Victoria Grant", "score": 90}
            ],
            common_mismatches=[
                "Timeline doesn't align with grant deadlines",
                "Project budget exceeds grant limits"
            ],
            suggested_improvements=[
                "Consider adjusting project timeline to match grant cycles",
                "Break down larger projects into fundable components"
            ]
        )
        
        return GrantDashboard(
            metrics=metrics,
            categories=categories,
            timeline=timeline,
            matching_insights=matching_insights,
            last_updated=now
        )
    except Exception as e:
        logger.error(f"Error generating dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating dashboard")

# Scraper Integration
async def run_scrapers_background(sources: List[str], db: Session):
    """Background task to run scrapers."""
    scrapers = {
        "business.gov.au": BusinessGovScraper(db),
        "grantconnect.gov.au": GrantConnectScraper(db)
    }
    
    for source in sources:
        if source in scrapers:
            try:
                logger.info(f"Running scraper for {source}")
                scraper = scrapers[source]
                grants = await scraper.scrape()
                scraper.save_grants(grants)
                logger.info(f"Successfully scraped {len(grants)} grants from {source}")
            except Exception as e:
                logger.error(f"Error running scraper for {source}: {str(e)}")

@router.post("/scrape", response_model=ScraperRunResponse)
async def run_scrapers(
    request: ScraperRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run grant scrapers to fetch new grant data."""
    try:
        available_sources = ["business.gov.au", "grantconnect.gov.au"]
        sources_to_run = request.sources or available_sources
        
        # Validate sources
        invalid_sources = [s for s in sources_to_run if s not in available_sources]
        if invalid_sources:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sources: {invalid_sources}. Available: {available_sources}"
            )
        
        # Add background task
        background_tasks.add_task(run_scrapers_background, sources_to_run, db)
        
        return ScraperRunResponse(
            started_at=datetime.utcnow(),
            sources=sources_to_run,
            status="started",
            message=f"Scraper job started for {len(sources_to_run)} sources"
        )
    except Exception as e:
        logger.error(f"Error starting scrapers: {str(e)}")
        raise HTTPException(status_code=500, detail="Error starting scrapers")

@router.get("/scrape/status")
async def get_scraper_status():
    """Get current scraper status."""
    # This would typically check a job queue or database
    return {
        "status": "idle",
        "last_run": None,
        "next_scheduled": None,
        "available_sources": ["business.gov.au", "grantconnect.gov.au"]
    } 