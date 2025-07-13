from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# Association tables
grant_tags = Table(
    "grant_tags",
    Base.metadata,
    Column("grant_id", Integer, ForeignKey("grants.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

class Tag(Base):
    """Model for project tags."""
    
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    
    # Relationships
    projects = relationship("Project", secondary="project_tags", back_populates="tags")
    # grants = relationship("Grant", secondary="grant_tags", back_populates="tags")  # Temporarily disabled
    tasks = relationship("Task", secondary="task_tags", back_populates="tags") 