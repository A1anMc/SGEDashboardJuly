from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, event, CheckConstraint, Enum, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    ARCHIVED = "archived"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(Base):
    """Task model for managing project tasks and assignments."""
    
    __tablename__ = "task"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False)
    priority = Column(String, nullable=False)
    
    # Time tracking
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), nullable=False)
    creator_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Additional data
    tags = Column(JSON, nullable=True)
    attachments = Column(JSON, nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="tasks")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    comments = relationship("TaskComment", back_populates="task", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="task", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            status.in_(["todo", "in_progress", "in_review", "done", "archived"]),
            name="task_status_check"
        ),
        CheckConstraint(
            priority.in_(["low", "medium", "high", "urgent"]),
            name="task_priority_check"
        ),
    )

    @property
    def total_time_spent(self) -> int:
        """Calculate total time spent in minutes from time entries."""
        return sum(entry.duration_minutes for entry in self.time_entries)

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        return bool(self.due_date and self.due_date < datetime.utcnow() and self.status not in [TaskStatus.DONE, TaskStatus.ARCHIVED])

class TaskComment(Base):
    """Model for task comments."""
    
    __tablename__ = "task_comment"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    parent_id = Column(Integer, ForeignKey("task_comment.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="task_comments")
    parent = relationship("TaskComment", remote_side=[id], backref="replies")
    
    # Add mentions and reactions
    mentions = Column(JSON, default=list)
    reactions = Column(JSON, default=dict, nullable=False)  # Format: {"emoji": [user_ids]}

class TimeEntry(Base):
    """Model for tracking time spent on tasks."""
    
    __tablename__ = "time_entry"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    task = relationship("Task", back_populates="time_entries")
    user = relationship("User", back_populates="time_entries")

@event.listens_for(TimeEntry, "after_insert")
@event.listens_for(TimeEntry, "after_delete")
def update_task_hours(mapper, connection, target):
    """Update task's actual_hours when time entries are added or removed"""
    task = target.task
    total_minutes = sum(entry.duration_minutes for entry in task.time_entries)
    task.actual_hours = total_minutes // 60 