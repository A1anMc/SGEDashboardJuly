from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class TagCategory(str, enum.Enum):
    """Categories for controlled vocabularies."""
    INDUSTRY = "industry"
    LOCATION = "location"
    ORG_TYPE = "org_type"
    FUNDING_PURPOSE = "funding_purpose"
    AUDIENCE = "audience"
    OTHER = "other"

# Association tables for many-to-many relationships
grant_tags = Table(
    'grant_tags',
    Base.metadata,
    Column('grant_id', Integer, ForeignKey('grants.id', ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"))
)

project_tags = Table(
    'project_tags',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('project.id', ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"))
)

class Tag(Base):
    """Tag model for controlled vocabularies."""
    
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    category = Column(SQLEnum(TagCategory), nullable=False, index=True)
    description = Column(String(500))
    
    # Optional parent-child relationship for hierarchical tags
    parent_id = Column(Integer, ForeignKey('tags.id', ondelete="SET NULL"), nullable=True)
    children = relationship("Tag", 
                          backref="parent",
                          remote_side=[id],
                          cascade="all, delete-orphan")
    
    # Synonyms for flexible matching
    synonyms = Column(String(1000))  # Comma-separated list
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey('user.id', ondelete="SET NULL"))
    
    # Relationships
    grants = relationship("Grant", secondary=grant_tags, back_populates="tags")
    projects = relationship("Project", secondary=project_tags, back_populates="tags")
    created_by = relationship("User")
    
    def __repr__(self):
        return f"<Tag {self.name} ({self.category})>"
    
    @property
    def synonym_list(self) -> List[str]:
        """Convert comma-separated synonyms to list."""
        return [s.strip() for s in self.synonyms.split(",")] if self.synonyms else []
    
    @synonym_list.setter
    def synonym_list(self, values: List[str]) -> None:
        """Convert list of synonyms to comma-separated string."""
        self.synonyms = ",".join(values) if values else None 