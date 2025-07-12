from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Grant(Base):
    """Grant model for tracking funding opportunities."""
    
    __tablename__ = "grants"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(100), index=True, nullable=False)
    source_url = Column(String(1000), nullable=True)
    application_url = Column(String(1000), nullable=True)
    contact_email = Column(String(255), nullable=True)
    
    # Financial details
    min_amount = Column(Numeric(10, 2), nullable=True)
    max_amount = Column(Numeric(10, 2), nullable=True)
    
    # Dates
    open_date = Column(DateTime, nullable=True, index=True)
    deadline = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Categorization
    industry_focus = Column(String(100), nullable=True, index=True)
    location_eligibility = Column(String(100), nullable=True, index=True)
    org_type_eligible = Column(JSON, nullable=True, default=list)
    funding_purpose = Column(JSON, nullable=True, default=list)
    audience_tags = Column(JSON, nullable=True, default=list)
    
    # Status and notes
    status = Column(String(50), nullable=False, default="draft", index=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_by = relationship("User", back_populates="grants")
    
    # Many-to-many relationship with tags
    tags = relationship("Tag", secondary="grant_tags", back_populates="grants")
    
    def __repr__(self):
        return f"<Grant {self.title}>"
    
    def calculate_match_score(self, project_profile: dict) -> dict:
        """Calculate how well this grant matches a project profile."""
        score = 0
        reasons = []
        
        # Check industry focus
        if self.industry_focus and project_profile.get("industry"):
            if self.industry_focus.lower() == project_profile["industry"].lower():
                score += 30
                reasons.append("Industry focus matches")
            else:
                reasons.append("Industry focus mismatch")
        
        # Check location eligibility
        if self.location_eligibility and project_profile.get("location"):
            if (self.location_eligibility.lower() == project_profile["location"].lower() or 
                self.location_eligibility.lower() == "national"):
                score += 20
                reasons.append("Location eligible")
            else:
                reasons.append("Location not eligible")
        
        # Check organization type
        if self.org_type_eligible and project_profile.get("org_type"):
            if project_profile["org_type"] in [t.lower() for t in self.org_type_eligible] or "any" in self.org_type_eligible:
                score += 20
                reasons.append("Organization type eligible")
            else:
                reasons.append("Organization type not eligible")
        
        # Check funding amount
        if project_profile.get("funding_needed"):
            funding_needed = float(project_profile["funding_needed"])
            if self.min_amount and funding_needed < float(self.min_amount):
                reasons.append("Funding amount below minimum")
            elif self.max_amount and funding_needed > float(self.max_amount):
                reasons.append("Funding amount above maximum")
            else:
                score += 30
                reasons.append("Funding amount within range")
        
        return {
            "grant_id": self.id,
            "title": self.title,
            "score": score,
            "reasons": reasons,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "amount_range": f"${self.min_amount or 0:,.2f} - ${self.max_amount or 0:,.2f}"
        } 