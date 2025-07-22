from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    organisation_name = Column(String(255), nullable=False)
    organisation_type = Column(String(100), nullable=False)
    industry_focus = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    website = Column(String(500), nullable=True)
    description = Column(String(1000), nullable=True)
    
    # Grant preferences
    preferred_funding_range_min = Column(Integer, nullable=True)
    preferred_funding_range_max = Column(Integer, nullable=True)
    preferred_industries = Column(JSON, nullable=True, default=list)
    preferred_locations = Column(JSON, nullable=True, default=list)
    preferred_org_types = Column(JSON, nullable=True, default=list)
    max_deadline_days = Column(Integer, nullable=True, default=90)
    min_grant_amount = Column(Integer, nullable=True, default=0)
    max_grant_amount = Column(Integer, nullable=True, default=1000000)
    
    # Notification preferences
    email_notifications = Column(String(50), default="weekly")
    deadline_alerts = Column(Integer, default=7)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, organisation='{self.organisation_name}')>" 