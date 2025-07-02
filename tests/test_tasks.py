import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.task import Task, TaskComment, TimeEntry, TaskStatus, TaskPriority
from app.models.user import User
from app.models.project import Project

@pytest.fixture
def test_user(db: Session) -> User:
    user = User(
        email="test@example.com",
        hashed_password="dummyhash",
        full_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_project(db: Session, test_user: User) -> Project:
    project = Project(
        title="Test Project",
        description="A test project",
        owner_id=test_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def test_create_task(db: Session, test_user: User, test_project: Project):
    # Create a basic task
    task = Task(
        title="Test Task",
        description="Test Description",
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        project_id=test_project.id,
        creator_id=test_user.id,
        assignee_id=test_user.id,
        due_date=datetime.utcnow() + timedelta(days=7),
        estimated_hours=4,
        tags=["test", "important"],
        attachments=[]
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Verify task was created correctly
    assert task.id is not None
    assert task.title == "Test Task"
    assert task.status == TaskStatus.TODO
    assert task.priority == TaskPriority.MEDIUM
    assert task.creator_id == test_user.id
    assert task.assignee_id == test_user.id
    assert task.project_id == test_project.id
    assert len(task.tags) == 2
    assert task.estimated_hours == 4
    assert task.actual_hours == 0

def test_task_status_update(db: Session, test_user: User, test_project: Project):
    # Create a task
    task = Task(
        title="Status Test Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        project_id=test_project.id,
        creator_id=test_user.id
    )
    db.add(task)
    db.commit()

    # Update status
    original_updated_at = task.updated_at
    task.status = TaskStatus.IN_PROGRESS
    db.commit()
    db.refresh(task)

    # Verify status change and updated_at timestamp
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.updated_at > original_updated_at

def test_task_comments(db: Session, test_user: User, test_project: Project):
    # Create a task
    task = Task(
        title="Comment Test Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        project_id=test_project.id,
        creator_id=test_user.id
    )
    db.add(task)
    db.commit()

    # Add a comment
    comment = TaskComment(
        task_id=task.id,
        user_id=test_user.id,
        content="Test comment"
    )
    db.add(comment)
    db.commit()
    db.refresh(task)

    # Verify comment
    assert len(task.comments) == 1
    assert task.comments[0].content == "Test comment"
    assert task.comments[0].user_id == test_user.id

def test_time_tracking(db: Session, test_user: User, test_project: Project):
    # Create a task
    task = Task(
        title="Time Tracking Test Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        project_id=test_project.id,
        creator_id=test_user.id,
        estimated_hours=4
    )
    db.add(task)
    db.commit()

    # Add time entry
    now = datetime.utcnow()
    time_entry = TimeEntry(
        task_id=task.id,
        user_id=test_user.id,
        duration_minutes=120,  # 2 hours
        description="Initial work",
        started_at=now - timedelta(hours=2),
        ended_at=now
    )
    db.add(time_entry)
    db.commit()

    # Update task's actual hours
    task.actual_hours = int(task.total_time_spent / 60)
    db.commit()
    db.refresh(task)

    # Verify time entry
    assert len(task.time_entries) == 1
    assert task.time_entries[0].duration_minutes == 120
    assert task.actual_hours == 2  # Should be updated based on time entries

def test_task_constraints(db: Session, test_user: User, test_project: Project):
    # Test invalid status
    with pytest.raises(Exception):  # Should raise a constraint violation
        task = Task(
            title="Invalid Status Task",
            status="invalid_status",  # Invalid status
            priority=TaskPriority.LOW,
            project_id=test_project.id,
            creator_id=test_user.id
        )
        db.add(task)
        db.commit()

    # Test invalid priority
    with pytest.raises(Exception):  # Should raise a constraint violation
        task = Task(
            title="Invalid Priority Task",
            status=TaskStatus.TODO,
            priority="invalid_priority",  # Invalid priority
            project_id=test_project.id,
            creator_id=test_user.id
        )
        db.add(task)
        db.commit()

def test_cascade_delete(db: Session, test_user: User, test_project: Project):
    # Create a task with comments and time entries
    task = Task(
        title="Cascade Test Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        project_id=test_project.id,
        creator_id=test_user.id
    )
    db.add(task)
    db.commit()

    # Add comment and time entry
    comment = TaskComment(task_id=task.id, user_id=test_user.id, content="Test comment")
    time_entry = TimeEntry(
        task_id=task.id,
        user_id=test_user.id,
        duration_minutes=60,
        started_at=datetime.utcnow(),
        ended_at=datetime.utcnow() + timedelta(hours=1)
    )
    db.add(comment)
    db.add(time_entry)
    db.commit()

    # Delete task
    db.delete(task)
    db.commit()

    # Verify cascade delete
    assert db.query(TaskComment).filter_by(task_id=task.id).first() is None
    assert db.query(TimeEntry).filter_by(task_id=task.id).first() is None 