from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()

@router.get("/")
async def list_tags(
    db: Session = Depends(get_db)
):
    """List tags endpoint."""
    # Placeholder for list tags logic
    return {"message": "List tags endpoint"}

@router.get("/{tag_id}")
async def get_tag(
    tag_id: int,
    db: Session = Depends(get_db)
):
    """Get tag by ID endpoint."""
    # Placeholder for get tag logic
    return {"message": "Get tag endpoint"} 