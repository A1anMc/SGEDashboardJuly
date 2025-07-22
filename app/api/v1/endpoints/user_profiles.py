from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user_profile import UserProfile
from app.models.grant import Grant
from app.schemas.user_profile import (
    UserProfileCreate, 
    UserProfileUpdate, 
    UserProfile, 
    UserProfileResponse,
    UserProfileMatch
)

router = APIRouter()

@router.post("/", response_model=UserProfileResponse)
def create_user_profile(
    profile_data: UserProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new user profile"""
    try:
        # For now, create a profile without user authentication
        # In a real app, this would be linked to the authenticated user
        profile = UserProfile(**profile_data.dict())
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        return UserProfileResponse(
            profile=profile,
            message="Profile created successfully"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating profile: {str(e)}"
        )

@router.get("/", response_model=UserProfileResponse)
def get_user_profile(db: Session = Depends(get_db)):
    """Get the current user's profile (for now, returns the first profile)"""
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile found. Please create a profile first."
        )
    
    return UserProfileResponse(
        profile=profile,
        message="Profile retrieved successfully"
    )

@router.put("/", response_model=UserProfileResponse)
def update_user_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update the current user's profile"""
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile found. Please create a profile first."
        )
    
    try:
        # Update only provided fields
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        profile.updated_at = datetime.now()
        db.commit()
        db.refresh(profile)
        
        return UserProfileResponse(
            profile=profile,
            message="Profile updated successfully"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

@router.get("/matching-grants", response_model=List[UserProfileMatch])
def get_matching_grants(db: Session = Depends(get_db)):
    """Get grants that match the user's profile preferences"""
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile found. Please create a profile first."
        )
    
    # Get all grants
    grants = db.query(Grant).filter(Grant.status == "open").all()
    matching_grants = []
    
    for grant in grants:
        match_score = 0
        match_reasons = []
        is_eligible = True
        
        # Check organization type eligibility
        if grant.org_type_eligible and profile.organization_type:
            if profile.organization_type in grant.org_type_eligible:
                match_score += 25
                match_reasons.append("Organization type matches")
            else:
                is_eligible = False
                match_reasons.append("Organization type not eligible")
        
        # Check industry focus
        if grant.industry_focus and profile.industry_focus:
            if grant.industry_focus == profile.industry_focus:
                match_score += 20
                match_reasons.append("Industry focus matches")
            elif grant.industry_focus in (profile.preferred_industries or []):
                match_score += 15
                match_reasons.append("Industry in preferences")
        
        # Check location eligibility
        if grant.location_eligibility and profile.location:
            if grant.location_eligibility == "National" or grant.location_eligibility == profile.location:
                match_score += 15
                match_reasons.append("Location eligible")
            elif grant.location_eligibility in (profile.preferred_locations or []):
                match_score += 10
                match_reasons.append("Location in preferences")
        
        # Check funding amount preferences
        if profile.min_grant_amount is not None and profile.max_grant_amount is not None:
            grant_min = grant.min_amount or 0
            grant_max = grant.max_amount or 0
            
            if grant_min >= profile.min_grant_amount and grant_max <= profile.max_grant_amount:
                match_score += 20
                match_reasons.append("Funding amount in preferred range")
            elif grant_min >= profile.min_grant_amount:
                match_score += 10
                match_reasons.append("Minimum funding meets preference")
        
        # Check deadline preferences
        if grant.deadline and profile.max_deadline_days:
            days_until_deadline = (grant.deadline - datetime.now()).days
            if days_until_deadline <= profile.max_deadline_days:
                match_score += 10
                match_reasons.append("Deadline within preferred timeframe")
        
        # Only include eligible grants with some match score
        if is_eligible and match_score > 0:
            matching_grants.append(UserProfileMatch(
                grant_id=grant.id,
                grant_title=grant.title,
                match_score=round(match_score, 1),
                match_reasons=match_reasons,
                is_eligible=is_eligible
            ))
    
    # Sort by match score (highest first)
    matching_grants.sort(key=lambda x: x.match_score, reverse=True)
    
    return matching_grants

@router.post("/seed-sample")
def seed_sample_profile(db: Session = Depends(get_db)):
    """Create a sample user profile for testing"""
    existing_profile = db.query(UserProfile).first()
    if existing_profile:
        return {
            "message": "Profile already exists",
            "profile_id": existing_profile.id
        }
    
    sample_profile = UserProfile(
        organization_name="TechStart Solutions",
        organization_type="Startup",
        industry_focus="technology",
        location="Sydney",
        website="https://techstart.com.au",
        description="Innovative technology startup focused on digital media solutions",
        preferred_funding_range_min=25000,
        preferred_funding_range_max=200000,
        preferred_industries=["technology", "digital media", "innovation"],
        preferred_locations=["Sydney", "Melbourne", "National"],
        preferred_org_types=["Startup", "SME"],
        max_deadline_days=60,
        min_grant_amount=25000,
        max_grant_amount=200000,
        email_notifications="weekly",
        deadline_alerts=7
    )
    
    try:
        db.add(sample_profile)
        db.commit()
        db.refresh(sample_profile)
        
        return {
            "message": "Sample profile created successfully",
            "profile_id": sample_profile.id,
            "organization": sample_profile.organization_name
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating sample profile: {str(e)}"
        ) 