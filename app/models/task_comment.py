from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.db.base import Base
from typing import List, Dict

class TaskComment(Base):
    """Model for task comments."""
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("task_comments.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    mentions = Column(JSON, nullable=True, default=list)
    
    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="comments")
    parent = relationship("TaskComment", remote_side=[id], back_populates="replies")
    replies = relationship("TaskComment", back_populates="parent", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="comment", cascade="all, delete-orphan")
    
    @property
    def reaction_summary(self) -> Dict[str, List[int]]:
        """Get a summary of reactions grouped by emoji."""
        summary = {}
        for reaction in self.reactions:
            if reaction.emoji not in summary:
                summary[reaction.emoji] = []
            summary[reaction.emoji].append(reaction.user_id)
        return summary 