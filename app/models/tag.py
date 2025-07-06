from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Tag(Base):
    """Tag model for categorizing projects and grants."""
    
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    category = Column(String(50), index=True, nullable=False)
    description = Column(String(500), nullable=True)
    synonyms = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Parent tag relationship
    parent_id = Column(Integer, ForeignKey("tags.id", ondelete="SET NULL"), nullable=True)
    parent = relationship("Tag", remote_side=[id], backref="children")
    
    # Creator relationship
    created_by_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    created_by = relationship("User")
    
    # Project relationship
    projects = relationship("Project", secondary="project_tags", back_populates="tags")
    
    # Grant relationship
    grants = relationship("Grant", secondary="grant_tags", back_populates="tags") 