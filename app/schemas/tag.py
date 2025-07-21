from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.tag import TagCategory

class TagBase(BaseModel):
    """Base schema for tag data."""
    name: str = Field(..., min_length=1, max_length=255)
    category: TagCategory
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None
    synonyms: Optional[List[str]] = None

class TagCreate(TagBase):
    """Schema for creating a new tag."""
    pass

class TagUpdate(BaseModel):
    """Schema for updating an existing tag."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[TagCategory] = None
    description: Optional[str] = Field(None, max_length=500)
    parent_id: Optional[int] = None
    synonyms: Optional[List[str]] = None

class Tag(TagBase):
    """Schema for tag response."""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    children: List["Tag"] = []
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Media Production",
                "category": "industry",
                "description": "Media and film production projects",
                "parent_id": None,
                "synonyms": ["film production", "content creation"],
                "created_at": "2024-03-20T10:00:00",
                "updated_at": "2024-03-20T10:00:00",
                "created_by_id": 1,
                "children": []
            }
        }

class TagWithRelations(Tag):
    """Schema for tag with related entities."""
    grant_count: int
    project_count: int 