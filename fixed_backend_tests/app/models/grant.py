from sqlalchemy import Column, Integer, String, Text
from app.db.base_class import Base

class GrantModel(Base):
    __tablename__ = "grants"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    source = Column(String)
    tags = Column(String)