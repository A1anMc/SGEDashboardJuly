from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import Base and all models to ensure they're registered
from app.db.base import Base  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.team_member import TeamMember  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.metric import Metric  # noqa: F401
from app.models.program_logic import ProgramLogic  # noqa: F401
from app.models.grant import Grant  # noqa: F401
from app.models.task import Task, TaskComment, TimeEntry  # noqa: F401

from app.api.v1.api import api_router
from app.db.session import engine

# Create all tables in the database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Shadow Goose Entertainment API",
    description="API for managing Shadow Goose Entertainment projects and resources",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Shadow Goose Entertainment API!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()} 