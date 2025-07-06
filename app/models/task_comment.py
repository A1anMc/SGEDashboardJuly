from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class TaskComment(Base):
    """Task comment model for threaded discussions on tasks."""
    
    __tablename__ = "task_comment"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Task relationship
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    task = relationship("Task", back_populates="comments")
    
    # User relationship
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    user = relationship("User", back_populates="task_comments")
    
    # Parent comment relationship for threading
    parent_id = Column(Integer, ForeignKey("task_comment.id", ondelete="CASCADE"), nullable=True)
    parent = relationship("TaskComment", remote_side=[id], backref="replies")
    
    # Additional metadata
    mentions = Column(JSON, nullable=True)
    reactions = Column(JSON, nullable=True) 