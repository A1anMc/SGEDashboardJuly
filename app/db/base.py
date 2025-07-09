# Import base class for SQLAlchemy models
from app.db.base_class import Base

# Import all models for SQLAlchemy to discover them
from app.models.user import User
from app.models.task import Task
from app.models.task_comment import TaskComment
from app.models.reaction import Reaction
from app.models.scraper_log import ScraperLog
from app.models.project import Project
from app.models.time_entry import TimeEntry
from app.models.tag import Tag
from app.models.project_tags import project_tags
from app.models.task_tags import task_tags
from app.models.team_member import TeamMember

# This file is used by Alembic for migrations and by the application for model discovery
# All models should be imported here to ensure they are discovered by SQLAlchemy 