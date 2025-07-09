from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Metric(Base):
    """Metric model for tracking project performance metrics."""
    
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), index=True, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="metrics") 