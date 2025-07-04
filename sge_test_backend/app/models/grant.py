from sqlalchemy import Column, Integer, String, DateTime, Text, func, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

# Association table for many-to-many relationship
grant_tags = Table(
    'grant_tags',
    Base.metadata,
    Column('grant_id', Integer, ForeignKey('grants.id', ondelete="CASCADE")),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"))
)

class Grant(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    deadline = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="draft")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    tags = relationship("Tag", secondary=grant_tags, back_populates="grants")

    def __repr__(self):
        return f"<Grant {self.title}>" 