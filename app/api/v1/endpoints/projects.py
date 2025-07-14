from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.deps import get_db  # Use consistent database dependency
from app.models.project import Project
from app.db.session import get_last_connection_error

router = APIRouter()

@router.get("/")
async def list_projects(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
):
    """List projects endpoint with proper error handling."""
    try:
        query = db.query(Project)
        
        if status:
            query = query.filter(Project.status == status)
        
        total = query.count()
        projects = query.offset(skip).limit(limit).all()
        
        return {
            "items": [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                    "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                    "status": getattr(project, 'status', 'active'),
                    "team_size": getattr(project, 'team_size', 0),
                }
                for project in projects
            ],
            "total": total,
            "page": skip // limit + 1,
            "size": limit,
            "has_next": skip + limit < total,
            "has_prev": skip > 0
        }
    except Exception as e:
        # Check for database connection issues
        conn_error = get_last_connection_error()
        if conn_error:
            raise HTTPException(
                status_code=503,
                detail={
                    "message": "Database connection error",
                    "error": str(conn_error.get("error")),
                    "last_attempt": datetime.fromtimestamp(conn_error.get("last_attempt", 0)).isoformat() if conn_error.get("last_attempt") else None
                }
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching projects: {str(e)}"
        )

@router.get("/{project_id}")
async def get_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Get project by ID endpoint with proper error handling."""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=404,
                detail=f"Project {project_id} not found"
            )
        
        return {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "updated_at": project.updated_at.isoformat() if project.updated_at else None,
            "status": getattr(project, 'status', 'active'),
            "team_size": getattr(project, 'team_size', 0),
        }
    except HTTPException:
        raise
    except Exception as e:
        # Check for database connection issues
        conn_error = get_last_connection_error()
        if conn_error:
            raise HTTPException(
                status_code=503,
                detail={
                    "message": "Database connection error",
                    "error": str(conn_error.get("error")),
                    "last_attempt": datetime.fromtimestamp(conn_error.get("last_attempt", 0)).isoformat() if conn_error.get("last_attempt") else None
                }
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching project {project_id}: {str(e)}"
        ) 