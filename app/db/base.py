# Import base class for SQLAlchemy models
from app.db.base_class import Base

# Import all models for SQLAlchemy to discover them
from app.models.user import User  # noqa: F401

# This file is used by Alembic for migrations and by the application for model discovery
# All models should be imported here to ensure they are discovered by SQLAlchemy 