from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class GrantBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    amount: Optional[float] = Field(None, ge=0)
    deadline: Optional[datetime] = None
    status: str = Field(..., pattern="^(open|closed|draft)$")
    tags: List[str] = Field(default_factory=list)
    source_url: Optional[str] = None
    source: str
    notes: Optional[str] = None

class GrantCreate(GrantBase):
    pass

class GrantUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    amount: Optional[float] = Field(None, ge=0)
    deadline: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(open|closed|draft)$")
    tags: Optional[List[str]] = None
    source_url: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None

class GrantResponse(GrantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GrantList(BaseModel):
    items: List[GrantResponse]
    total: int
    page: int
    size: int 