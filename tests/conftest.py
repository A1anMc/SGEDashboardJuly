import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine
from datetime import datetime
from alembic import command
from alembic.config import Config

# Import Base and all models to ensure they're registered
from app.db.base import Base
from app.models.user import User  # noqa: F401
from app.models.project import Project  # noqa: F401
from app.models.task import Task, TaskComment, TimeEntry  # noqa: F401

from app.main import app
from app.core.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token

# Enable SQLite foreign key support
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create engine for SQLite in-memory database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Create session factory
TestingSessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    # Drop all tables if they exist
    Base.metadata.drop_all(bind=engine)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for the test
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        TestingSessionLocal.remove()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Create a test client using the test database."""
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear the dependency override after the test
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Add access token
    access_token = create_access_token({"sub": str(user.id)})
    user.access_token = access_token
    
    return user

@pytest.fixture(scope="function")
def test_user2(db):
    """Create another test user."""
    user = User(
        email="test2@example.com",
        hashed_password="hashed_password",
        full_name="Test User 2",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Add access token
    access_token = create_access_token({"sub": str(user.id)})
    user.access_token = access_token
    
    return user

@pytest.fixture(scope="function")
def test_project(db, test_user):
    """Create a test project."""
    project = Project(
        title="Test Project",
        description="Test Project Description",
        status="active",
        owner_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@pytest.fixture(scope="function")
def test_task(db, test_user, test_project):
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="Test Description",
        status="todo",
        priority="medium",
        project_id=test_project.id,
        creator_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@pytest.fixture(scope="function")
def test_comment(db, test_user, test_task):
    """Create a test comment."""
    comment = TaskComment(
        task_id=test_task.id,
        user_id=test_user.id,
        content="Test Comment",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        reactions={},
        mentions=[]
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment