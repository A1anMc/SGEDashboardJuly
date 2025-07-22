from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core import deps
from app.schemas.user_profile import UserProfile, UserProfileCreate, UserProfileUpdate
from app.models.user_profile import UserProfile as UserProfileModel
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[UserProfile])
def get_user_profiles(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> List[UserProfile]:
    """Get all user profiles."""
    user_profiles = db.query(UserProfileModel).offset(skip).limit(limit).all()
    return user_profiles

@router.get("/me", response_model=UserProfile)
def get_my_profile(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> UserProfile:
    """Get current user's profile."""
    user_profile = db.query(UserProfileModel).filter(
        UserProfileModel.user_id == current_user.id
    ).first()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return user_profile

@router.get("/{user_profile_id}", response_model=UserProfile)
def get_user_profile(
    user_profile_id: int,
    db: Session = Depends(deps.get_db),
) -> UserProfile:
    """Get a specific user profile by ID."""
    user_profile = db.query(UserProfileModel).filter(
        UserProfileModel.id == user_profile_id
    ).first()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return user_profile

@router.post("/", response_model=UserProfile)
def create_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_profile_in: UserProfileCreate,
    current_user: User = Depends(deps.get_current_user),
) -> UserProfile:
    """Create a new user profile."""
    # Check if user already has a profile
    existing_profile = db.query(UserProfileModel).filter(
        UserProfileModel.user_id == current_user.id
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a profile"
        )
    
    user_profile = UserProfileModel(
        **user_profile_in.model_dump(),
        user_id=current_user.id
    )
    db.add(user_profile)
    db.commit()
    db.refresh(user_profile)
    return user_profile

@router.put("/me", response_model=UserProfile)
def update_my_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_profile_in: UserProfileUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> UserProfile:
    """Update current user's profile."""
    user_profile = db.query(UserProfileModel).filter(
        UserProfileModel.user_id == current_user.id
    ).first()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    update_data = user_profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_profile, field, value)
    
    db.add(user_profile)
    db.commit()
    db.refresh(user_profile)
    return user_profile

@router.put("/{user_profile_id}", response_model=UserProfile)
def update_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_profile_id: int,
    user_profile_in: UserProfileUpdate,
) -> UserProfile:
    """Update a specific user profile."""
    user_profile = db.query(UserProfileModel).filter(
        UserProfileModel.id == user_profile_id
    ).first()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    update_data = user_profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user_profile, field, value)
    
    db.add(user_profile)
    db.commit()
    db.refresh(user_profile)
    return user_profile

@router.delete("/{user_profile_id}")
def delete_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_profile_id: int,
) -> dict:
    """Delete a user profile."""
    user_profile = db.query(UserProfileModel).filter(
        UserProfileModel.id == user_profile_id
    ).first()
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    db.delete(user_profile)
    db.commit()
    return {"message": "User profile deleted successfully"} 