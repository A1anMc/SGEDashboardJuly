from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db_session
from app.models.grant import Grant

router = APIRouter()

@router.get("/")
async def list_grants(
    db: Session = Depends(get_db_session)
):
    """List grants endpoint."""
    # Placeholder for list grants logic
    return {"message": "List grants endpoint"}

@router.get("/{grant_id}")
async def get_grant(
    grant_id: int,
    db: Session = Depends(get_db_session)
):
    """Get grant by ID endpoint."""
    # Placeholder for get grant logic
    return {"message": "Get grant endpoint"} 