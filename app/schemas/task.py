from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority
from app.schemas.task_comment import TaskCommentResponse

class TaskBase(BaseModel):
    """Base schema for tasks."""
    title: str
    description: Optional[str] = None
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    project_id: int
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: Optional[List[str]] = []

class TaskCreate(TaskBase):
    """Schema for creating tasks."""
    pass

class TaskUpdate(BaseModel):
    """Schema for updating tasks."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    tags: Optional[List[str]] = None

class TaskResponse(TaskBase):
    """Schema for task responses."""
    id: int
    creator_id: int
    actual_hours: float
    created_at: datetime
    updated_at: datetime
    comments: List[TaskCommentResponse] = []
    total_time_spent: float
    comment_count: int
    reaction_summary: Dict[str, List[int]] = {}
    
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    """Base schema for comments."""
    content: str
    parent_id: Optional[int] = None
    mentions: Optional[List[str]] = None

class CommentCreate(CommentBase):
    """Schema for creating a comment."""
    task_id: int

class CommentUpdate(BaseModel):
    """Schema for updating a comment."""
    content: Optional[str] = None
    mentions: Optional[List[str]] = None

class CommentResponse(CommentBase):
    """Schema for comment responses."""
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    reactions: Optional[Dict[str, List[int]]] = None
    
    class Config:
        from_attributes = True

class ReactionCreate(BaseModel):
    """Schema for creating a reaction."""
    emoji: str
    comment_id: int

class ReactionResponse(ReactionCreate):
    """Schema for reaction responses."""
    id: int
    user_id: int
    
    class Config:
        from_attributes = True

class TimeEntryBase(BaseModel):
    """Base schema for time entry data."""
    duration_minutes: int
    description: Optional[str] = None
    started_at: datetime
    ended_at: datetime

class TimeEntryCreate(TimeEntryBase):
    """Schema for creating a new time entry."""
    pass

class TimeEntryResponse(TimeEntryBase):
    """Schema for time entry responses."""
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 