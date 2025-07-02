from sqlalchemy.orm import Session

from app.db.base_class import Base
from app.db.session import engine

# Import all models to ensure they are registered with SQLAlchemy
from app.models.grant import GrantModel
from app.models.user import User
from app.models.team_member import TeamMember
from app.models.project import Project
from app.models.metric import Metric
from app.models.program_logic import ProgramLogic

def init_db() -> None:
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine) 