from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[dict])
async def list_users(
    db: Session = Depends(get_db)
):
    """List all users."""
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        for user in users
    ]

@router.get("/me")
async def get_current_user(
    db: Session = Depends(get_db)
):
    """Get current user endpoint."""
    # Placeholder for get current user logic
    return {"message": "Get current user endpoint"}

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user by ID endpoint."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    } 