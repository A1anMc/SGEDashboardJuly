from datetime import datetime
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

class IndustryFocus(str, Enum):
    MEDIA = "media"
    CREATIVE_ARTS = "creative_arts"
    TECHNOLOGY = "technology"
    GENERAL = "general"

class LocationEligibility(str, Enum):
    NATIONAL = "Australia"
    VIC = "VIC"
    NSW = "NSW"
    QLD = "QLD"
    SA = "SA"
    WA = "WA"
    TAS = "TAS"
    NT = "NT"
    ACT = "ACT"

class OrgType(str, Enum):
    SOCIAL_ENTERPRISE = "social_enterprise"
    NFP = "not_for_profit"
    SME = "small_medium_enterprise"
    STARTUP = "startup"
    ANY = "any"

class GrantStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    DRAFT = "draft"

class GrantBase(BaseModel):
    """Base schema for grant data."""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1, max_length=255)
    
    # Matching criteria
    industry_focus: IndustryFocus
    location_eligibility: LocationEligibility
    org_type_eligible: List[OrgType] = Field(default_factory=list)
    funding_purpose: List[str] = Field(default_factory=list)
    audience_tags: List[str] = Field(default_factory=list)
    
    # Timing and amount
    open_date: datetime
    deadline: datetime
    min_amount: Optional[int] = Field(None, ge=0)
    max_amount: Optional[int] = Field(None, ge=0)
    
    # Status and metadata
    status: GrantStatus = GrantStatus.ACTIVE
    
    # Additional data
    application_url: Optional[str] = Field(None, max_length=500)
    contact_email: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

    @validator('max_amount')
    def validate_max_amount(cls, v, values):
        if v is not None and 'min_amount' in values and values['min_amount'] is not None:
            if v < values['min_amount']:
                raise ValueError('max_amount must be greater than or equal to min_amount')
        return v

    @validator('deadline')
    def validate_deadline(cls, v, values):
        if 'open_date' in values and values['open_date'] is not None:
            if v <= values['open_date']:
                raise ValueError('deadline must be after open_date')
        return v

class GrantCreate(GrantBase):
    """Schema for creating a new grant."""
    pass

class GrantUpdate(BaseModel):
    """Schema for updating a grant."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    source: Optional[str] = Field(None, min_length=1, max_length=255)
    
    # Matching criteria
    industry_focus: Optional[IndustryFocus] = None
    location_eligibility: Optional[LocationEligibility] = None
    org_type_eligible: Optional[List[OrgType]] = None
    funding_purpose: Optional[List[str]] = None
    audience_tags: Optional[List[str]] = None
    
    # Timing and amount
    open_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    min_amount: Optional[int] = Field(None, ge=0)
    max_amount: Optional[int] = Field(None, ge=0)
    
    # Status and metadata
    status: Optional[GrantStatus] = None
    
    # Additional data
    application_url: Optional[str] = Field(None, max_length=500)
    contact_email: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None

class GrantResponse(GrantBase):
    """Schema for grant responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    # Computed fields for matching
    match_score: Optional[int] = None
    matched_criteria: Optional[List[str]] = None
    missing_criteria: Optional[List[str]] = None
    
    class Config:
        from_attributes = True

class GrantList(BaseModel):
    """Schema for paginated grant list responses."""
    items: List[GrantResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

class GrantFilters(BaseModel):
    """Schema for grant filtering parameters."""
    industry_focus: Optional[IndustryFocus] = None
    location_eligibility: Optional[LocationEligibility] = None
    status: Optional[GrantStatus] = None
    min_amount: Optional[int] = Field(None, ge=0)
    max_amount: Optional[int] = Field(None, ge=0)
    deadline_before: Optional[datetime] = None
    deadline_after: Optional[datetime] = None
    search: Optional[str] = None
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=100)

class GrantMatchResult(BaseModel):
    """Schema for grant matching results."""
    grant_id: int
    score: int = Field(..., ge=0, le=100)
    matched_criteria: List[str]
    missing_criteria: List[str]
    grant_title: str
    deadline: datetime
    max_amount: Optional[int] = None

class ProjectProfile(BaseModel):
    """Schema for project profile used in grant matching."""
    location: str
    org_type: str
    funding_purposes: List[str] = Field(default_factory=list)
    themes: List[str] = Field(default_factory=list)
    timeline: Dict[str, Union[str, None]] = Field(default_factory=dict)

class GrantMetrics(BaseModel):
    """Schema for grant dashboard metrics."""
    total_active: int = Field(..., ge=0)
    total_amount_available: float = Field(..., ge=0)
    upcoming_deadlines: int = Field(..., ge=0)
    avg_match_score: float = Field(..., ge=0, le=100)

class GrantsByCategory(BaseModel):
    """Schema for grants grouped by categories."""
    by_industry: Dict[str, int] = Field(default_factory=dict)
    by_location: Dict[str, int] = Field(default_factory=dict)
    by_org_type: Dict[str, int] = Field(default_factory=dict)
    by_funding_range: Dict[str, int] = Field(default_factory=dict)

class DeadlineGroup(BaseModel):
    """Schema for groups of grants by deadline period."""
    grants: List[Dict] = Field(default_factory=list)
    total_amount: float = Field(..., ge=0)
    count: int = Field(..., ge=0)

class GrantTimeline(BaseModel):
    """Schema for grant timeline view."""
    this_week: DeadlineGroup
    next_week: DeadlineGroup
    this_month: DeadlineGroup
    next_month: DeadlineGroup
    later: DeadlineGroup

class MatchingInsights(BaseModel):
    """Schema for grant matching insights."""
    best_matches: List[Dict] = Field(default_factory=list)
    common_mismatches: List[str] = Field(default_factory=list)
    suggested_improvements: List[str] = Field(default_factory=list)

class GrantDashboard(BaseModel):
    """Schema for complete grant dashboard data."""
    metrics: GrantMetrics
    categories: GrantsByCategory
    timeline: GrantTimeline
    matching_insights: MatchingInsights
    last_updated: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "metrics": {
                    "total_active": 45,
                    "total_amount_available": 5750000.0,
                    "upcoming_deadlines": 12,
                    "avg_match_score": 72.5
                },
                "categories": {
                    "by_industry": {
                        "media": 20,
                        "creative_arts": 15,
                        "technology": 5,
                        "general": 5
                    },
                    "by_location": {
                        "VIC": 15,
                        "NSW": 10,
                        "Australia": 20
                    },
                    "by_org_type": {
                        "social_enterprise": 25,
                        "not_for_profit": 15,
                        "small_medium_enterprise": 5
                    },
                    "by_funding_range": {
                        "0-10k": 10,
                        "10k-50k": 20,
                        "50k-100k": 10,
                        "100k+": 5
                    }
                },
                "timeline": {
                    "this_week": {
                        "grants": [
                            {"id": 1, "title": "Arts Grant 2024", "deadline": "2024-03-25T00:00:00", "amount": 50000}
                        ],
                        "total_amount": 150000.0,
                        "count": 3
                    },
                    "next_week": {"grants": [], "total_amount": 0.0, "count": 0},
                    "this_month": {"grants": [], "total_amount": 250000.0, "count": 5},
                    "next_month": {"grants": [], "total_amount": 500000.0, "count": 8},
                    "later": {"grants": [], "total_amount": 1000000.0, "count": 15}
                },
                "matching_insights": {
                    "best_matches": [
                        {"grant_id": 1, "title": "Screen Australia Fund", "score": 95},
                        {"grant_id": 2, "title": "Creative Victoria Grant", "score": 90}
                    ],
                    "common_mismatches": [
                        "Timeline doesn't align with grant deadlines",
                        "Project budget exceeds grant limits"
                    ],
                    "suggested_improvements": [
                        "Consider adjusting project timeline to match grant cycles",
                        "Break down larger projects into fundable components"
                    ]
                },
                "last_updated": "2024-03-20T10:00:00"
            }
        }

class ScraperRunRequest(BaseModel):
    """Schema for scraper run requests."""
    sources: Optional[List[str]] = None
    force_refresh: bool = False

class ScraperRunResponse(BaseModel):
    """Schema for scraper run responses."""
    started_at: datetime
    sources: List[str]
    status: str
    message: str