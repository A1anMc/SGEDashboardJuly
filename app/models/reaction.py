from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Reaction(Base):
    """Model for emoji reactions on comments."""
    
    __tablename__ = "reaction"
    
    id = Column(Integer, primary_key=True, index=True)
    emoji = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    comment_id = Column(Integer, ForeignKey("task_comment.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="reactions")
    comment = relationship("TaskComment", back_populates="reactions") 