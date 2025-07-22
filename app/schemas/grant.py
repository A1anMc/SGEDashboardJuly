from datetime import datetime
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field, EmailStr, HttpUrl

class GrantBase(BaseModel):
    """Base schema for grant data."""
    title: str
    description: Optional[str] = None
    source: str
    source_url: Optional[HttpUrl] = None
    application_url: Optional[HttpUrl] = None
    contact_email: Optional[EmailStr] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    open_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    industry_focus: Optional[str] = None
    location_eligibility: Optional[str] = None
    org_type_eligible: Optional[List[str]] = None
    funding_purpose: Optional[List[str]] = None
    audience_tags: Optional[List[str]] = []
    status: str = Field(default="active", pattern="^(active|inactive|expired|open|closed|draft)$")
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class GrantCreate(GrantBase):
    """Schema for creating a new grant."""
    pass

class GrantUpdate(GrantBase):
    """Schema for updating an existing grant."""
    title: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None

class GrantResponse(GrantBase):
    """Schema for grant responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class GrantFilters(BaseModel):
    """Schema for grant filtering parameters."""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=10, ge=1, le=100)
    industry_focus: Optional[str] = None
    location_eligibility: Optional[str] = None
    status: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    deadline_before: Optional[datetime] = None
    deadline_after: Optional[datetime] = None
    search: Optional[str] = None

class GrantList(BaseModel):
    """Schema for paginated grant list."""
    items: List[GrantResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

class ProjectProfile(BaseModel):
    """Schema for project profile used in grant matching."""
    industry: str
    location: str
    org_type: str
    funding_needed: float
    project_timeline: Optional[Dict[str, datetime]] = None
    focus_areas: Optional[List[str]] = None

class GrantMatchResult(BaseModel):
    """Schema for grant matching results."""
    grant_id: int
    title: str
    score: int
    reasons: List[str]
    deadline: Optional[str]
    amount_range: str

class GrantData(BaseModel):
    """Schema for grant data in groups."""
    id: int
    title: str
    amount: Optional[float] = None
    deadline: Optional[datetime] = None
    status: str
    source: str

class DeadlineGroup(BaseModel):
    """Schema for grouped grants by deadline."""
    grants: List[Dict[str, Union[str, int, float, datetime, None]]]
    total_amount: float
    count: int

    class Config:
        arbitrary_types_allowed = True

class GrantTimeline(BaseModel):
    """Schema for grant timeline view."""
    this_week: DeadlineGroup
    next_week: DeadlineGroup
    this_month: DeadlineGroup
    next_month: DeadlineGroup
    later: DeadlineGroup

class GrantsByCategory(BaseModel):
    """Schema for grants grouped by category."""
    by_industry: Dict[str, int]
    by_location: Dict[str, int]
    by_org_type: Dict[str, int]
    by_funding_range: Dict[str, int]

class GrantMetrics(BaseModel):
    """Schema for grant dashboard metrics."""
    total_active: int
    total_amount_available: float
    upcoming_deadlines: int
    avg_match_score: float

class MatchingInsights(BaseModel):
    """Schema for grant matching insights."""
    best_matches: List[Dict[str, Union[str, int, float, datetime, None]]]
    common_mismatches: List[str]
    suggested_improvements: List[str]

    class Config:
        arbitrary_types_allowed = True

class GrantDashboard(BaseModel):
    """Schema for comprehensive grant dashboard."""
    metrics: GrantMetrics
    categories: GrantsByCategory
    timeline: GrantTimeline
    matching_insights: MatchingInsights
    last_updated: datetime

class ScraperStatus(BaseModel):
    """Schema for scraper status."""
    status: str
    last_run: Optional[datetime] = None
    next_scheduled: Optional[datetime] = None
    available_sources: List[str]

    class Config:
        from_attributes = True

class ScraperRunRequest(BaseModel):
    """Schema for scraper run requests."""
    source: str
    keywords: Optional[List[str]] = []
    tags: Optional[List[str]] = []

class ScraperRunResponse(BaseModel):
    """Schema for scraper run responses."""
    message: str
    status: str = "accepted"