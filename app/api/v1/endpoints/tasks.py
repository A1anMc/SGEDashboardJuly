from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db_session
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.task_comment import TaskComment
from app.models.user import User
from app.core.auth import get_current_user
from app.schemas.task_comment import TaskCommentCreate, TaskCommentUpdate, TaskCommentResponse
from app.schemas.task import TaskCreate, TaskResponse
from app.core.email import send_task_assignment_email

router = APIRouter()

@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db_session),
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
        tags=task.tags,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
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

@router.post("/comments", response_model=TaskCommentResponse)
async def create_comment(
    comment: TaskCommentCreate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new comment on a task."""
    # Verify task exists
    task = db.query(Task).filter(Task.id == comment.task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Create comment
    db_comment = TaskComment(
        task_id=comment.task_id,
        user_id=current_user.id,
        content=comment.content,
        parent_id=comment.parent_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        reactions={}
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    return db_comment

@router.get("/comments/task/{task_id}", response_model=List[TaskCommentResponse])
async def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db_session)
):
    """Get all comments for a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    comments = db.query(TaskComment).filter(TaskComment.task_id == task_id).all()
    return comments

@router.put("/comments/{comment_id}", response_model=TaskCommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: TaskCommentUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Update a comment."""
    db_comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Verify ownership
    if db_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment"
        )
    
    # Update comment
    db_comment.content = comment_update.content
    db_comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_comment)
    
    return db_comment

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment."""
    db_comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Verify ownership
    if db_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    db.delete(db_comment)
    db.commit()

@router.post("/comments/{comment_id}/reactions/{reaction_type}")
async def add_reaction(
    comment_id: int,
    reaction_type: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Add a reaction to a comment."""
    db_comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Add reaction
    if not db_comment.reactions:
        db_comment.reactions = {}
    
    if reaction_type not in db_comment.reactions:
        db_comment.reactions[reaction_type] = []
    
    if current_user.id not in db_comment.reactions[reaction_type]:
        db_comment.reactions[reaction_type].append(current_user.id)
        db.commit()
        db.refresh(db_comment)
    
    return db_comment.reactions

@router.delete("/comments/{comment_id}/reactions/{reaction_type}")
async def remove_reaction(
    comment_id: int,
    reaction_type: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Remove a reaction from a comment."""
    db_comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Remove reaction
    if db_comment.reactions and reaction_type in db_comment.reactions:
        if current_user.id in db_comment.reactions[reaction_type]:
            db_comment.reactions[reaction_type].remove(current_user.id)
            if not db_comment.reactions[reaction_type]:
                del db_comment.reactions[reaction_type]
            db.commit()
            db.refresh(db_comment)
    
    return db_comment.reactions 