from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class TeamMember(Base):
    """TeamMember model for managing project team members."""
    
    __tablename__ = "team_members"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False)  # e.g., "developer", "designer", "manager"
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="team_memberships")
    project = relationship("Project", back_populates="team_members") 