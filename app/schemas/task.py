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
    """Schema for creating a task."""
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
    """Schema for task response."""
    id: int
    creator_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskCommentBase(BaseModel):
    """Base schema for task comments."""
    content: str = Field(..., min_length=1)

class TaskCommentCreate(TaskCommentBase):
    """Schema for creating a task comment."""
    pass

class TaskCommentResponse(TaskCommentBase):
    """Schema for task comment response."""
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TimeEntryBase(BaseModel):
    """Base schema for time entries."""
    duration_minutes: int = Field(..., gt=0)
    description: Optional[str] = None
    started_at: datetime
    ended_at: datetime

class TimeEntryCreate(TimeEntryBase):
    """Schema for creating a time entry."""
    pass

class TimeEntryResponse(TimeEntryBase):
    """Schema for time entry response."""
    id: int
    task_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None
    mentions: List[int] = Field(default_factory=list)  # List of user IDs mentioned

class CommentCreate(CommentBase):
    task_id: int

class CommentUpdate(BaseModel):
    content: Optional[str] = None
    mentions: Optional[List[int]] = None

class ReactionUpdate(BaseModel):
    emoji: str
    action: str = Field(..., pattern='^(add|remove)$')  # Only allow 'add' or 'remove'

class CommentResponse(CommentBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    replies: List['CommentResponse'] = []
    reactions: Dict[str, List[int]] = Field(default_factory=dict)

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def from_orm(cls, obj):
        # Ensure reactions is initialized as a dict
        if obj.reactions is None:
            obj.reactions = {}
        return super().from_orm(obj)

# This is needed for the recursive type hint to work
CommentResponse.model_rebuild() 