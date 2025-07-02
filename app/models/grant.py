from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped
from app.db.base_class import Base
import enum

class IndustryFocus(str, enum.Enum):
    MEDIA = "media"
    CREATIVE_ARTS = "creative_arts"
    TECHNOLOGY = "technology"
    GENERAL = "general"

class LocationEligibility(str, enum.Enum):
    NATIONAL = "Australia"
    VIC = "VIC"
    NSW = "NSW"
    QLD = "QLD"
    SA = "SA"
    WA = "WA"
    TAS = "TAS"
    NT = "NT"
    ACT = "ACT"

class OrgType(str, enum.Enum):
    SOCIAL_ENTERPRISE = "social_enterprise"
    NFP = "not_for_profit"
    SME = "small_medium_enterprise"
    STARTUP = "startup"
    ANY = "any"

class Grant(Base):
    """Grant model with matching algorithm fields."""
    
    __tablename__ = "grants"

    # Basic Information
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    source = Column(String(255), nullable=False)
    
    # Matching Criteria Fields
    industry_focus = Column(SQLEnum(IndustryFocus), nullable=False)
    location_eligibility = Column(SQLEnum(LocationEligibility), nullable=False)
    org_type_eligible = Column(JSON, nullable=False, default=list)  # List of OrgType
    funding_purpose = Column(JSON, nullable=False, default=list)    # List of purposes
    audience_tags = Column(JSON, nullable=False, default=list)      # List of audience types
    
    # Timing and Amount
    open_date = Column(DateTime, nullable=False)
    deadline = Column(DateTime, nullable=False)
    min_amount = Column(Integer, nullable=True)
    max_amount = Column(Integer, nullable=True)
    
    # Status and Metadata
    status = Column(String(50), nullable=False, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional Data
    application_url = Column(String(500), nullable=True)
    contact_email = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    def calculate_match_score(self, project_profile: Dict) -> Dict:
        """
        Calculate match score between grant and project profile.
        Returns score and explanation of matching criteria.
        """
        score = 0
        matched_criteria = []
        missing_criteria = []
        
        # Industry Focus (30 points)
        if self.industry_focus in [IndustryFocus.MEDIA, IndustryFocus.CREATIVE_ARTS]:
            score += 30
            matched_criteria.append(f"industry_focus: {self.industry_focus}")
        else:
            missing_criteria.append("industry_focus_mismatch")
        
        # Location Eligibility (20 points)
        if self.location_eligibility in [LocationEligibility.NATIONAL, LocationEligibility(project_profile["location"])]:
            score += 20
            matched_criteria.append(f"location_eligibility: {self.location_eligibility}")
        else:
            missing_criteria.append("location_mismatch")
        
        # Organization Type (15 points)
        if project_profile["org_type"] in self.org_type_eligible:
            score += 15
            matched_criteria.append(f"org_type_eligible: {project_profile['org_type']}")
        else:
            missing_criteria.append("org_type_mismatch")
        
        # Funding Purpose (15 points)
        project_purposes = set(project_profile.get("funding_purposes", []))
        if project_purposes.intersection(set(self.funding_purpose)):
            score += 15
            matched_criteria.append("funding_purpose_match")
        else:
            missing_criteria.append("funding_purpose_mismatch")
        
        # Audience Alignment (10 points)
        project_themes = set(project_profile.get("themes", []))
        if project_themes.intersection(set(self.audience_tags)):
            score += 10
            matched_criteria.append("audience_alignment")
        else:
            missing_criteria.append("audience_mismatch")
        
        # Timeline Match (10 points)
        project_start = datetime.fromisoformat(project_profile["timeline"]["start"])
        if self.open_date <= project_start <= self.deadline:
            score += 10
            matched_criteria.append("timeline_match")
        else:
            missing_criteria.append("timeline_mismatch")
        
        return {
            "grant_id": self.id,
            "score": score,
            "matched_criteria": matched_criteria,
            "missing_criteria": missing_criteria,
            "grant_title": self.title,
            "deadline": self.deadline.isoformat(),
            "max_amount": self.max_amount
        }

    def __repr__(self):
        return f"<Grant {self.title}>" 