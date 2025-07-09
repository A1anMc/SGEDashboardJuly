
from app.db.base_class import Base
from app.db.session import engine

# Import all models to ensure they are registered with SQLAlchemy

def init_db() -> None:
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine) 