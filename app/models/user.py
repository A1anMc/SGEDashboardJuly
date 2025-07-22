from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    """Model for users."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Project relationships
    owned_projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    team_memberships = relationship("TeamMember", back_populates="user", cascade="all, delete-orphan")
    
    # Task relationships
    created_tasks = relationship("Task", foreign_keys="[Task.creator_id]", back_populates="creator")
    assigned_tasks = relationship("Task", foreign_keys="[Task.assignee_id]", back_populates="assignee")
    
    # Comment relationships
    comments = relationship("TaskComment", back_populates="user", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="user", cascade="all, delete-orphan")
    
    # Time tracking
    time_entries = relationship("TimeEntry", back_populates="user", cascade="all, delete-orphan")
    
    # Grant relationships
    # grants = relationship("Grant", back_populates="created_by", foreign_keys="[Grant.created_by_id]")  # Temporarily disabled
    
    # Profile relationship
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan") 