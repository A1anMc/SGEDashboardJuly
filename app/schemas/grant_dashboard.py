from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class GrantMetrics(BaseModel):
    """Analytics for grant opportunities."""
    total_active: int = Field(..., description="Total number of active grants")
    total_amount_available: float = Field(..., description="Total funding amount available")
    upcoming_deadlines: int = Field(..., description="Number of grants due in next 30 days")
    avg_match_score: float = Field(..., description="Average match score across all projects")
    
class GrantsByCategory(BaseModel):
    """Distribution of grants by category."""
    by_industry: Dict[str, int] = Field(..., description="Grants count by industry")
    by_location: Dict[str, int] = Field(..., description="Grants count by location")
    by_org_type: Dict[str, int] = Field(..., description="Grants count by organization type")
    by_funding_range: Dict[str, int] = Field(..., description="Grants count by funding range")

class DeadlineGroup(BaseModel):
    """Group of grants by deadline period."""
    grants: List[Dict] = Field(..., description="List of grants in this period")
    total_amount: float = Field(..., description="Total funding available")
    count: int = Field(..., description="Number of grants")

class GrantTimeline(BaseModel):
    """Timeline view of grants by deadline."""
    this_week: DeadlineGroup
    next_week: DeadlineGroup
    this_month: DeadlineGroup
    next_month: DeadlineGroup
    later: DeadlineGroup

class MatchingInsights(BaseModel):
    """Insights about grant matching."""
    best_matches: List[Dict] = Field(..., description="Top matching grants across projects")
    common_mismatches: List[str] = Field(..., description="Common reasons for low match scores")
    suggested_improvements: List[str] = Field(..., description="Suggestions to improve match scores")

class GrantDashboard(BaseModel):
    """Complete grant dashboard data."""
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
                            {"id": 1, "title": "Arts Grant 2024", "deadline": "2024-03-25", "amount": 50000}
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