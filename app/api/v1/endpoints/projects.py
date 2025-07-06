from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db_session
from app.models.project import Project

router = APIRouter()

@router.get("/")
async def list_projects(
    db: Session = Depends(get_db_session)
):
    """List projects endpoint."""
    # Placeholder for list projects logic
    return {"message": "List projects endpoint"}

@router.get("/{project_id}")
async def get_project(
    project_id: int,
    db: Session = Depends(get_db_session)
):
    """Get project by ID endpoint."""
    # Placeholder for get project logic
    return {"message": "Get project endpoint"} 