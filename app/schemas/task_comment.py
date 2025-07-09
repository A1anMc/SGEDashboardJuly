from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class TaskCommentBase(BaseModel):
    """Base schema for task comments."""
    content: str
    task_id: int
    parent_id: Optional[int] = None
    mentions: Optional[List[int]] = []

class TaskCommentCreate(TaskCommentBase):
    """Schema for creating task comments."""
    pass

class TaskCommentUpdate(BaseModel):
    """Schema for updating task comments."""
    content: str
    mentions: Optional[List[int]] = []

class TaskCommentResponse(TaskCommentBase):
    """Schema for task comment responses."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    reactions: Dict[str, List[int]] = {}
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @property
    def reaction_count(self) -> int:
        """Get total number of reactions."""
        return sum(len(users) for users in self.reactions.values()) 