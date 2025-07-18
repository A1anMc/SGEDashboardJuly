from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from app.db.session import get_db
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.task_comment import TaskComment
from app.models.reaction import Reaction
from app.models.user import User
from app.core.auth import get_current_user
from app.schemas.task_comment import TaskCommentCreate, TaskCommentUpdate, TaskCommentResponse
from app.schemas.task import TaskCreate, TaskResponse
from app.core.email import send_task_assignment_email

router = APIRouter()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new task."""
    # Create task
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status or TaskStatus.TODO,
        priority=task.priority or TaskPriority.MEDIUM,
        estimated_hours=task.estimated_hours,
        actual_hours=0,
        due_date=task.due_date,
        project_id=task.project_id,
        creator_id=current_user.id,
        assignee_id=task.assignee_id,
        tags=[],  # Initialize as empty list
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Add tags if provided
    if task.tags:
        db_task.tags = task.tags
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Send email notification if task is assigned
    if db_task.assignee_id:
        assignee = db.query(User).filter(User.id == db_task.assignee_id).first()
        if assignee:
            await send_task_assignment_email(
                email_to=[assignee.email],
                task_title=db_task.title,
                task_description=db_task.description,
                assignee_name=assignee.full_name
            )
    
    return db_task

@router.get("/")
async def list_tasks(
    db: Session = Depends(get_db)
):
    """List tasks endpoint."""
    # Placeholder for list tasks logic
    return {"message": "List tasks endpoint"}

@router.get("/{task_id}")
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """Get task by ID endpoint."""
    # Placeholder for get task logic
    return {"message": "Get task endpoint"}

# Comment endpoints moved to app/api/v1/endpoints/comments.py

@router.post("/comments/{comment_id}/reactions/{emoji}", response_model=Dict[str, List[int]])
async def add_reaction(
    comment_id: int,
    emoji: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a reaction to a comment."""
    db_comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if reaction already exists
    existing_reaction = db.query(Reaction).filter(
        Reaction.comment_id == comment_id,
        Reaction.user_id == current_user.id,
        Reaction.emoji == emoji
    ).first()
    
    if existing_reaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reaction already exists"
        )
    
    # Create new reaction
    reaction = Reaction(
        emoji=emoji,
        user_id=current_user.id,
        comment_id=comment_id
    )
    db.add(reaction)
    db.commit()
    
    # Get all reactions for this comment grouped by emoji
    reactions = db.query(Reaction).filter(Reaction.comment_id == comment_id).all()
    reaction_dict = {}
    for r in reactions:
        if r.emoji not in reaction_dict:
            reaction_dict[r.emoji] = []
        reaction_dict[r.emoji].append(r.user_id)
    
    return reaction_dict

@router.delete("/comments/{comment_id}/reactions/{emoji}", response_model=Dict[str, List[int]])
async def remove_reaction(
    comment_id: int,
    emoji: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a reaction from a comment."""
    db_comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Find and remove reaction
    reaction = db.query(Reaction).filter(
        Reaction.comment_id == comment_id,
        Reaction.user_id == current_user.id,
        Reaction.emoji == emoji
    ).first()
    
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )
    
    db.delete(reaction)
    db.commit()
    
    # Get all remaining reactions for this comment grouped by emoji
    reactions = db.query(Reaction).filter(Reaction.comment_id == comment_id).all()
    reaction_dict = {}
    for r in reactions:
        if r.emoji not in reaction_dict:
            reaction_dict[r.emoji] = []
        reaction_dict[r.emoji].append(r.user_id)
    
    return reaction_dict 