"""
Seed script to initialize the database with test data.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import get_password_hash
from app.models.base import (
    User,
    Task,
    Project,
    Grant,
    Tag,
    TeamMember,
    TaskComment,
    TimeEntry,
    Reaction
)

def seed_database():
    """Seed the database with initial data."""
    with get_db() as db:
        # Create test users
        users = create_test_users(db)
        
        # Create test projects
        projects = create_test_projects(db, users)
        
        # Create test tasks
        tasks = create_test_tasks(db, users, projects)
        
        # Create test grants
        grants = create_test_grants(db)
        
        # Create test tags
        tags = create_test_tags(db)
        
        # Create test team members
        team_members = create_test_team_members(db, users, projects)
        
        db.commit()

def create_test_users(db: Session) -> list[User]:
    """Create test users."""
    users = [
        User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_superuser=True,
            is_active=True
        ),
        User(
            email="user@example.com",
            hashed_password=get_password_hash("user123"),
            full_name="Regular User",
            is_superuser=False,
            is_active=True
        )
    ]
    
    for user in users:
        db.add(user)
    
    db.flush()
    return users

def create_test_projects(db: Session, users: list[User]) -> list[Project]:
    """Create test projects."""
    projects = [
        Project(
            name="Website Redesign",
            description="Complete overhaul of the company website",
            status="in_progress",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=30),
            owner_id=users[0].id
        ),
        Project(
            name="Mobile App Development",
            description="New mobile app for grant management",
            status="planning",
            start_date=datetime.now() + timedelta(days=7),
            end_date=datetime.now() + timedelta(days=90),
            owner_id=users[1].id
        )
    ]
    
    for project in projects:
        db.add(project)
    
    db.flush()
    return projects

def create_test_tasks(db: Session, users: list[User], projects: list[Project]) -> list[Task]:
    """Create test tasks."""
    tasks = [
        Task(
            title="Design Homepage",
            description="Create new homepage design",
            status="in_progress",
            priority="high",
            due_date=datetime.now() + timedelta(days=7),
            creator_id=users[0].id,
            assignee_id=users[1].id,
            project_id=projects[0].id
        ),
        Task(
            title="Implement User Authentication",
            description="Set up user authentication system",
            status="todo",
            priority="high",
            due_date=datetime.now() + timedelta(days=14),
            creator_id=users[0].id,
            assignee_id=users[1].id,
            project_id=projects[1].id
        )
    ]
    
    for task in tasks:
        db.add(task)
    
    db.flush()
    return tasks

def create_test_grants(db: Session) -> list[Grant]:
    """Create test grants."""
    grants = [
        Grant(
            title="Business Innovation Grant",
            description="Grant for innovative business projects",
            amount_range="$10,000 - $50,000",
            open_date=datetime.now(),
            close_date=datetime.now() + timedelta(days=90),
            status="open",
            industry_focus="Technology",
            location_eligibility="Australia"
        ),
        Grant(
            title="Research Development Fund",
            description="Funding for research projects",
            amount_range="$50,000 - $200,000",
            open_date=datetime.now() + timedelta(days=30),
            close_date=datetime.now() + timedelta(days=120),
            status="upcoming",
            industry_focus="Research",
            location_eligibility="Australia"
        )
    ]
    
    for grant in grants:
        db.add(grant)
    
    db.flush()
    return grants

def create_test_tags(db: Session) -> list[Tag]:
    """Create test tags."""
    tags = [
        Tag(name="frontend", description="Frontend development tasks"),
        Tag(name="backend", description="Backend development tasks"),
        Tag(name="urgent", description="Urgent tasks"),
        Tag(name="bug", description="Bug fixes"),
        Tag(name="feature", description="New features")
    ]
    
    for tag in tags:
        db.add(tag)
    
    db.flush()
    return tags

def create_test_team_members(db: Session, users: list[User], projects: list[Project]) -> list[TeamMember]:
    """Create test team members."""
    team_members = [
        TeamMember(
            user_id=users[0].id,
            project_id=projects[0].id,
            role="project_manager"
        ),
        TeamMember(
            user_id=users[1].id,
            project_id=projects[0].id,
            role="developer"
        ),
        TeamMember(
            user_id=users[0].id,
            project_id=projects[1].id,
            role="developer"
        ),
        TeamMember(
            user_id=users[1].id,
            project_id=projects[1].id,
            role="project_manager"
        )
    ]
    
    for team_member in team_members:
        db.add(team_member)
    
    db.flush()
    return team_members

if __name__ == "__main__":
    seed_database() 