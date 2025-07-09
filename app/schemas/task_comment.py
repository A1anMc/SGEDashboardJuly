from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class TaskCommentBase(BaseModel):
    """Base schema for task comments."""
    content: str
    parent_id: Optional[int] = None

class TaskCommentCreate(TaskCommentBase):
    """Schema for creating a task comment."""
    task_id: int

class TaskCommentUpdate(BaseModel):
    """Schema for updating a task comment."""
    content: str

class TaskCommentResponse(TaskCommentBase):
    """Schema for task comment responses."""
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    reactions: Optional[Dict[str, List[int]]] = None
    
    class Config:
        from_attributes = True 