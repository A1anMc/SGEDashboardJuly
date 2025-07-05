from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    """Base schema for task data."""
    title: str
    description: Optional[str] = None
    status: str = Field(default="todo", pattern="^(todo|in_progress|in_review|done|archived)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    due_date: Optional[datetime] = None
    project_id: int
    assignee_id: Optional[int] = None
    tags: Optional[List[str]] = None
    attachments: Optional[List[str]] = None

class TaskCreate(TaskBase):
    """Schema for creating a new task."""
    pass

class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(todo|in_progress|in_review|done|archived)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    due_date: Optional[datetime] = None
    project_id: Optional[int] = None
    assignee_id: Optional[int] = None
    tags: Optional[List[str]] = None
    attachments: Optional[List[str]] = None

class TaskResponse(TaskBase):
    """Schema for task responses."""
    id: int
    creator_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
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

class ReactionUpdate(BaseModel):
    """Schema for updating reactions."""
    emoji: str
    action: str = Field(pattern="^(add|remove)$")

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