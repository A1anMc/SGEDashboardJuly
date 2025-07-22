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

@router.get("/test", response_model=dict)
def test_user_profiles() -> dict:
    """Test endpoint for user profiles without authentication."""
    try:
        # Create our own database session
        from app.db.session import get_session_local
        from sqlalchemy import text
        
        SessionLocal = get_session_local()
        db = SessionLocal()
        
        try:
            # Step 1: Test basic database connection
            result = db.execute(text("SELECT 1 as test"))
            basic_test = result.scalar()
            
            # Step 2: Test if user_profiles table exists
            result = db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'user_profiles'
                )
            """))
            table_exists = result.scalar()
            
            # Step 3: Test count query
            if table_exists:
                result = db.execute(text("SELECT COUNT(*) FROM user_profiles"))
                total_profiles = result.scalar()
            else:
                total_profiles = 0
            
            # Step 4: Test select query
            if table_exists and total_profiles > 0:
                result = db.execute(text("SELECT id FROM user_profiles LIMIT 1"))
                first_profile = result.fetchone()
                first_profile_id = first_profile[0] if first_profile else None
            else:
                first_profile_id = None
            
            return {
                "status": "success",
                "basic_test": basic_test,
                "table_exists": table_exists,
                "total_profiles": total_profiles,
                "has_profiles": total_profiles > 0,
                "first_profile_id": first_profile_id,
                "message": "User profiles endpoint working correctly"
            }
        finally:
            db.close()
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": "User profiles endpoint error"
        } 