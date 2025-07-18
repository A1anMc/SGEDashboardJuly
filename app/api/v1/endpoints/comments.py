from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from app.db.session import get_db
from app.models.task_comment import TaskComment
from app.models.reaction import Reaction
from app.models.task import Task
from app.models.user import User
from app.core.auth import get_current_user
from app.schemas.task_comment import TaskCommentCreate, TaskCommentUpdate, TaskCommentResponse

router = APIRouter()

@router.post("/", response_model=TaskCommentResponse)
async def create_comment(
    comment: TaskCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new comment."""
    # Verify task exists
    task = db.query(Task).filter(Task.id == comment.task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify parent comment if provided
    if comment.parent_id:
        parent_comment = db.query(TaskComment).filter(TaskComment.id == comment.parent_id).first()
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
        if parent_comment.task_id != comment.task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment must belong to the same task"
            )
    
    # Create comment
    db_comment = TaskComment(
        task_id=comment.task_id,
        user_id=current_user.id,
        content=comment.content,
        parent_id=comment.parent_id,
        mentions=comment.mentions or [],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Convert to response model
    return TaskCommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        task_id=db_comment.task_id,
        user_id=db_comment.user_id,
        parent_id=db_comment.parent_id,
        mentions=db_comment.mentions or [],
        created_at=db_comment.created_at,
        updated_at=db_comment.updated_at,
        reactions=db_comment.reaction_summary
    )

@router.get("/task/{task_id}", response_model=List[TaskCommentResponse])
async def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all comments for a task."""
    comments = db.query(TaskComment).filter(TaskComment.task_id == task_id).all()
    return [
        TaskCommentResponse(
            id=comment.id,
            content=comment.content,
            task_id=comment.task_id,
            user_id=comment.user_id,
            parent_id=comment.parent_id,
            mentions=comment.mentions or [],
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            reactions=comment.reaction_summary
        )
        for comment in comments
    ]

@router.put("/{comment_id}", response_model=TaskCommentResponse)
async def update_comment(
    comment_id: int,
    comment_update: TaskCommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a comment."""
    db_comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if db_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment"
        )
    
    db_comment.content = comment_update.content
    db_comment.mentions = comment_update.mentions or []
    db_comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_comment)
    
    return TaskCommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        task_id=db_comment.task_id,
        user_id=db_comment.user_id,
        parent_id=db_comment.parent_id,
        mentions=db_comment.mentions or [],
        created_at=db_comment.created_at,
        updated_at=db_comment.updated_at,
        reactions=db_comment.reaction_summary
    )

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a comment."""
    db_comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if db_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )
    
    db.delete(db_comment)
    db.commit()

@router.post("/{comment_id}/reactions/{emoji}", response_model=Dict[str, List[int]])
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
        # Remove reaction if it exists (toggle behavior)
        db.delete(existing_reaction)
    else:
        # Create new reaction
        reaction = Reaction(
            emoji=emoji,
            user_id=current_user.id,
            comment_id=comment_id
        )
        db.add(reaction)
    
    db.commit()
    db.refresh(db_comment)
    
    return db_comment.reaction_summary

@router.delete("/{comment_id}/reactions/{emoji}", response_model=Dict[str, List[int]])
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
    db.refresh(db_comment)
    
    return db_comment.reaction_summary 