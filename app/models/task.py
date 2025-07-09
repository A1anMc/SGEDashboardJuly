from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLAlchemyEnum, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.enums import TaskStatus, TaskPriority
from app.models.task_tags import task_tags
from enum import Enum as PyEnum
from typing import List, Dict

class TaskStatus(str, PyEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class TaskPriority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(Base):
    """Task model for tracking work items."""
    
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLAlchemyEnum(TaskStatus), nullable=False, default=TaskStatus.TODO)
    priority = Column(SQLAlchemyEnum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM)
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=False, default=0)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Project relationship
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    project = relationship("Project", back_populates="tasks")
    
    # User relationships
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    
    assignee_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    
    # Comment relationship
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    
    # Time entry relationship
    time_entries = relationship("TimeEntry", back_populates="task", cascade="all, delete-orphan")
    
    # Additional metadata
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks", collection_class=list)
    attachments = Column(JSON, nullable=True)

    @property
    def total_time_spent(self) -> int:
        """Calculate total time spent in minutes from time entries."""
        return sum(entry.duration_minutes for entry in self.time_entries)

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        return bool(self.due_date and self.due_date < datetime.utcnow() and self.status not in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]) 
    
    @property
    def total_time_spent(self) -> float:
        """Calculate total time spent on task in minutes."""
        return sum(entry.duration_minutes for entry in self.time_entries)
    
    @property
    def comment_count(self) -> int:
        """Get total number of comments on task."""
        return len(self.comments)
    
    @property
    def reaction_summary(self) -> Dict[str, List[int]]:
        """Get summary of all reactions on task comments."""
        summary = {}
        for comment in self.comments:
            for emoji, users in comment.reaction_summary.items():
                if emoji not in summary:
                    summary[emoji] = []
                summary[emoji].extend(users)
        return summary 