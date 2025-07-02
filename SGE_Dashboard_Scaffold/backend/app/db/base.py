from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr

# Import base class for SQLAlchemy models
from app.db.base_class import Base

# Import all models for SQLAlchemy to discover them
from app.models.user import User  # noqa: F401
from app.models.team_member import TeamMember  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.metric import Metric  # noqa: F401
from app.models.program_logic import ProgramLogic  # noqa: F401
from app.models.grant import GrantModel  # noqa: F401

# This file is used by Alembic for migrations and by the application for model discovery
# All models should be imported here to ensure they are discovered by SQLAlchemy

@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() 