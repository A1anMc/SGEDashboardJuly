from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from app.models.task import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    """Base schema for tasks."""
    title: str
    description: Optional[str] = None
    status: Optional[str] = TaskStatus.PENDING
    priority: Optional[str] = TaskPriority.MEDIUM
    estimated_hours: Optional[int] = None
    due_date: Optional[datetime] = None
    project_id: int
    assignee_id: Optional[int] = None
    tags: Optional[Dict] = None

class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass

class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    tags: Optional[Dict] = None

class TaskResponse(TaskBase):
    """Schema for task responses."""
    id: int
    creator_id: Optional[int]
    actual_hours: int
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    """Base schema for comment data."""
    content: str
    parent_id: Optional[int] = None

class CommentCreate(CommentBase):
    """Schema for creating a new comment."""
    pass

class CommentUpdate(BaseModel):
    """Schema for updating a comment."""
    content: Optional[str] = None

class CommentResponse(CommentBase):
    """Schema for comment responses."""
    id: int
    task_id: int
    user_id: int
    reactions: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime
    
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