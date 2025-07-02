from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class ProgramLogic(Base):
    __tablename__ = "program_logic"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    outcome = Column(Text, nullable=False)
    impact = Column(Text, nullable=False)
    
    # Relationships
    project = relationship("Project", back_populates="program_logic") 