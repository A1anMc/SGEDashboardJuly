from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Grant(Base):
    """Grant model for tracking funding opportunities."""
    
    __tablename__ = "grants"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(10, 2), nullable=True)
    source = Column(String(100), index=True, nullable=False)
    url = Column(String(1000), nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(50), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Creator relationship
    created_by_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    created_by = relationship("User")
    
    # Tag relationship
    tags = relationship("Tag", secondary="grant_tags", back_populates="grants") 