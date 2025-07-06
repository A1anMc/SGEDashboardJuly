from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db_session
from app.models.task import Task

router = APIRouter()

@router.get("/")
async def list_tasks(
    db: Session = Depends(get_db_session)
):
    """List tasks endpoint."""
    # Placeholder for list tasks logic
    return {"message": "List tasks endpoint"}

@router.get("/{task_id}")
async def get_task(
    task_id: int,
    db: Session = Depends(get_db_session)
):
    """Get task by ID endpoint."""
    # Placeholder for get task logic
    return {"message": "Get task endpoint"} 