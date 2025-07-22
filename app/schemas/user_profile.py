from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class UserProfileBase(BaseModel):
    organisation_name: str = Field(..., min_length=1, max_length=255)
    organisation_type: str = Field(..., min_length=1, max_length=100)
    industry_focus: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    
    # Grant preferences
    preferred_funding_range_min: Optional[int] = Field(None, ge=0)
    preferred_funding_range_max: Optional[int] = Field(None, ge=0)
    preferred_industries: Optional[List[str]] = Field(default_factory=list)
    preferred_locations: Optional[List[str]] = Field(default_factory=list)
    preferred_org_types: Optional[List[str]] = Field(default_factory=list)
    max_deadline_days: Optional[int] = Field(90, ge=1, le=365)
    min_grant_amount: Optional[int] = Field(0, ge=0)
    max_grant_amount: Optional[int] = Field(1000000, ge=0)
    
    # Notification preferences
    email_notifications: str = Field("weekly", pattern="^(daily|weekly|monthly|never)$")
    deadline_alerts: int = Field(7, ge=1, le=30)

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(BaseModel):
    organisation_name: Optional[str] = Field(None, min_length=1, max_length=255)
    organisation_type: Optional[str] = Field(None, min_length=1, max_length=100)
    industry_focus: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=1000)
    
    # Grant preferences
    preferred_funding_range_min: Optional[int] = Field(None, ge=0)
    preferred_funding_range_max: Optional[int] = Field(None, ge=0)
    preferred_industries: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    preferred_org_types: Optional[List[str]] = None
    max_deadline_days: Optional[int] = Field(None, ge=1, le=365)
    min_grant_amount: Optional[int] = Field(None, ge=0)
    max_grant_amount: Optional[int] = Field(None, ge=0)
    
    # Notification preferences
    email_notifications: Optional[str] = Field(None, pattern="^(daily|weekly|monthly|never)$")
    deadline_alerts: Optional[int] = Field(None, ge=1, le=30)

class UserProfileInDB(UserProfileBase):
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserProfile(UserProfileInDB):
    pass 