from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Project(Base):
    """Project model for organizing tasks and tracking progress."""
    
    __tablename__ = "project"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    budget = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Owner relationship
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    owner = relationship("User", back_populates="projects")
    
    # Task relationship
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    
    # Tag relationship
    tags = relationship("Tag", secondary="project_tags", back_populates="projects") 