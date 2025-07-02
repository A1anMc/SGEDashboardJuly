from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.models.grant import Grant
from app.schemas.project_profile import ProjectProfile
from app.schemas.grant_dashboard import GrantDashboard, GrantMetrics, GrantsByCategory, GrantTimeline, DeadlineGroup, MatchingInsights
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/match")
async def match_grants(
    project_profile: ProjectProfile,
    min_score: Optional[int] = Query(60, description="Minimum match score (0-100)"),
    limit: Optional[int] = Query(10, description="Maximum number of matches to return"),
    db: Session = Depends(get_db)
) -> List[dict]:
    """
    Match grants against a project profile.
    Returns sorted list of grants with match scores and explanations.
    """
    # Get all active grants
    grants = db.query(Grant).filter(Grant.status == "active").all()
    
    # Calculate match scores for all grants
    matches = []
    for grant in grants:
        match_result = grant.calculate_match_score(project_profile.dict())
        if match_result["score"] >= min_score:
            matches.append(match_result)
    
    # Sort by score descending and limit results
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:limit]

@router.get("/{grant_id}/match-details")
async def get_grant_match_details(
    grant_id: int,
    project_profile: ProjectProfile,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get detailed matching information for a specific grant.
    """
    grant = db.query(Grant).filter(Grant.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Grant not found")
    
    return grant.calculate_match_score(project_profile.dict())

@router.get("/dashboard", response_model=GrantDashboard)
async def get_grant_dashboard(db: Session = Depends(get_db)):
    """
    Get comprehensive grant dashboard data including metrics, categories, timeline, and insights.
    """
    # Get all active grants
    grants = db.query(Grant).filter(Grant.is_active == True).all()
    
    # Calculate metrics
    total_active = len(grants)
    total_amount = sum(grant.amount for grant in grants if grant.amount)
    now = datetime.now()
    upcoming = len([g for g in grants if g.deadline and (g.deadline - now).days <= 30])
    avg_score = sum(g.match_score for g in grants if g.match_score) / total_active if total_active > 0 else 0
    
    metrics = GrantMetrics(
        total_active=total_active,
        total_amount_available=total_amount,
        upcoming_deadlines=upcoming,
        avg_match_score=avg_score
    )
    
    # Calculate categories
    by_industry = {}
    by_location = {}
    by_org_type = {}
    by_funding_range = {}
    
    for grant in grants:
        # Industry counts
        if grant.industry:
            by_industry[grant.industry] = by_industry.get(grant.industry, 0) + 1
            
        # Location counts
        if grant.location:
            by_location[grant.location] = by_location.get(grant.location, 0) + 1
            
        # Organization type counts
        if grant.org_type:
            by_org_type[grant.org_type] = by_org_type.get(grant.org_type, 0) + 1
            
        # Funding range counts
        amount = grant.amount or 0
        range_key = "0-10k" if amount < 10000 else \
                   "10k-50k" if amount < 50000 else \
                   "50k-100k" if amount < 100000 else "100k+"
        by_funding_range[range_key] = by_funding_range.get(range_key, 0) + 1
    
    categories = GrantsByCategory(
        by_industry=by_industry,
        by_location=by_location,
        by_org_type=by_org_type,
        by_funding_range=by_funding_range
    )
    
    # Build timeline groups
    def group_grants(grants_list, start_date, end_date) -> DeadlineGroup:
        filtered = [
            {
                "id": g.id,
                "title": g.title,
                "deadline": g.deadline,
                "amount": g.amount
            }
            for g in grants_list
            if g.deadline and start_date <= g.deadline <= end_date
        ]
        return DeadlineGroup(
            grants=filtered,
            total_amount=sum(g["amount"] for g in filtered if g["amount"]),
            count=len(filtered)
        )
    
    this_week_end = now + timedelta(days=7)
    next_week_end = now + timedelta(days=14)
    this_month_end = now + timedelta(days=30)
    next_month_end = now + timedelta(days=60)
    
    timeline = GrantTimeline(
        this_week=group_grants(grants, now, this_week_end),
        next_week=group_grants(grants, this_week_end, next_week_end),
        this_month=group_grants(grants, next_week_end, this_month_end),
        next_month=group_grants(grants, this_month_end, next_month_end),
        later=group_grants(grants, next_month_end, now + timedelta(days=365))
    )
    
    # Generate insights
    best_matches = [
        {"grant_id": g.id, "title": g.title, "score": g.match_score}
        for g in sorted(grants, key=lambda x: x.match_score or 0, reverse=True)[:5]
    ]
    
    # Analyze common mismatches
    common_mismatches = []
    if any(g.deadline and g.deadline < now for g in grants):
        common_mismatches.append("Some grants have expired deadlines")
    if any(g.match_score and g.match_score < 50 for g in grants):
        common_mismatches.append("Several grants have low match scores")
        
    # Generate suggestions
    suggestions = [
        "Update project profiles regularly to improve match scores",
        "Set up email alerts for new matching grants",
        "Review and adjust project timelines based on grant deadlines"
    ]
    
    matching_insights = MatchingInsights(
        best_matches=best_matches,
        common_mismatches=common_mismatches,
        suggested_improvements=suggestions
    )
    
    return GrantDashboard(
        metrics=metrics,
        categories=categories,
        timeline=timeline,
        matching_insights=matching_insights,
        last_updated=now
    ) 