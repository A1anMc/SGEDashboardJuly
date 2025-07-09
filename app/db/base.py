"""SQLAlchemy models."""
from app.db.base_class import Base

# Import models in dependency order
from app.models.user import User
from app.models.project import Project
from app.models.team_member import TeamMember
from app.models.task import Task
from app.models.task_comment import TaskComment
from app.models.reaction import Reaction
from app.models.tag import Tag
from app.models.task_tags import task_tags
from app.models.project_tags import project_tags
from app.models.grant import Grant
from app.models.scraper_log import ScraperLog
from app.models.time_entry import TimeEntry
from app.models.metric import Metric
from app.models.program_logic import ProgramLogic

# All models should be imported here to ensure they are registered with SQLAlchemy 