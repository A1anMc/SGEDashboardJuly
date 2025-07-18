import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

# Set up test environment before importing any app modules
from tests.test_config import setup_test_env
setup_test_env()

# Import all models to ensure proper initialization
from app.db.base import Base
from app.models.user import User
from app.models.project import Project
from app.models.team_member import TeamMember
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.task_comment import TaskComment
from app.models.reaction import Reaction
from app.models.tag import Tag
from app.models.grant import Grant
from app.models.time_entry import TimeEntry
from app.models.metric import Metric
from app.models.program_logic import ProgramLogic
from app.core.auth import create_access_token, get_current_user
from app.core.config import settings
from app.main import app
from app.db.session import get_db

# Create test database engine
test_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Enable foreign key support based on database type
@event.listens_for(Engine, "connect")
def set_foreign_keys(dbapi_connection, connection_record):
    if settings.TESTING:
        cursor = dbapi_connection.cursor()
        if 'sqlite' in str(test_engine.url):
            cursor.execute("PRAGMA foreign_keys=ON")
        elif 'postgresql' in str(test_engine.url):
            cursor.execute("SET session_replication_role = 'replica';")
        cursor.close()

# Create test session factory
TestingSessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
)

@pytest.fixture(scope="function")
def db():
    """Test database session."""
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Get session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        TestingSessionLocal.remove()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password="dummyhash",
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_user2(db):
    """Create another test user."""
    user = User(
        email="test2@example.com",
        hashed_password="dummyhash",
        full_name="Test User 2",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_token(test_user):
    """Create a test JWT token."""
    return create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=30)
    )

@pytest.fixture
def client(db):
    """Test client with database session."""
    def override_get_db():
        try:
            yield db
        finally:
            pass  # Session cleanup is handled by db fixture
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def authorized_client(client, test_token, test_user):
    """Create an authorized test client."""
    # Mock get_current_user dependency
    async def override_get_current_user():
        return test_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {test_token}"
    }
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def test_project(db, test_user):
    """Create a test project."""
    project = Project(
        name="Test Project",
        description="Test Description",
        owner_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@pytest.fixture
def test_task(db, test_user, test_project):
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="Test Description",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        project_id=test_project.id,
        creator_id=test_user.id,
        assignee_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task