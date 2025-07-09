from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session

router = APIRouter()

@router.get("/me")
async def get_current_user(
    db: Session = Depends(get_db_session)
):
    """Get current user endpoint."""
    # Placeholder for get current user logic
    return {"message": "Get current user endpoint"}

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db_session)
):
    """Get user by ID endpoint."""
    # Placeholder for get user logic
    return {"message": "Get user endpoint"} 