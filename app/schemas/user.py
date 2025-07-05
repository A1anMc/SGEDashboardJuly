from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserResponse(UserBase):
    """Schema for user API responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True