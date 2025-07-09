from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session

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