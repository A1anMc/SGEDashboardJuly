# Import base class for SQLAlchemy models
from app.db.base_class import Base

# Import all models for SQLAlchemy to discover them
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.task_comment import TaskComment
from app.models.time_entry import TimeEntry
from app.models.tag import Tag
from app.models.grant import Grant
from app.models.team_member import TeamMember
from app.models.metric import Metric

# This file is used by Alembic for migrations and by the application for model discovery
# All models should be imported here to ensure they are discovered by SQLAlchemy 