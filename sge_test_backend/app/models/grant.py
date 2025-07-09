from sqlalchemy import Column, Integer, String, DateTime, Text, func
from app.db.base import Base

class Grant(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    deadline = Column(DateTime, nullable=True)
    tags = Column(String(500), nullable=True)  # Stored as comma-separated values
    status = Column(String(50), nullable=False, default="draft")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Grant {self.title}>"

    @property
    def tags_list(self) -> list[str]:
        """Convert comma-separated tags string to list."""
        return [tag.strip() for tag in self.tags.split(",")] if self.tags else []

    @tags_list.setter
    def tags_list(self, tags: list[str]) -> None:
        """Convert list of tags to comma-separated string."""
        self.tags = ",".join(tags) if tags else None 