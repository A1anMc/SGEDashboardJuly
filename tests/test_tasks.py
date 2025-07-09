import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.task_comment import TaskComment
from app.models.time_entry import TimeEntry
from app.models.user import User
from app.models.project import Project
from app.models.tag import Tag

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
        name="Test Project",
        description="A test project",
        status="active",
        owner_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def test_create_task(db: Session, test_user: User, test_project: Project):
    # Create tags first
    test_tag = Tag(name="test")
    important_tag = Tag(name="important")
    db.add(test_tag)
    db.add(important_tag)
    db.commit()
    
    # Create a basic task
    task = Task(
        title="Test Task",
        description="Test Description",
        status=TaskStatus.TODO.value,
        priority=TaskPriority.MEDIUM.value,
        project_id=test_project.id,
        creator_id=test_user.id,
        assignee_id=test_user.id,
        due_date=datetime.utcnow() + timedelta(days=7),
        estimated_hours=4,
        tags=[test_tag, important_tag],
        attachments=[]
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Verify task was created correctly
    assert task.id is not None
    assert task.title == "Test Task"
    assert task.status == TaskStatus.TODO.value
    assert task.priority == TaskPriority.MEDIUM.value
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
        status=TaskStatus.TODO.value,
        priority=TaskPriority.LOW.value,
        project_id=test_project.id,
        creator_id=test_user.id
    )
    db.add(task)
    db.commit()

    # Update status
    original_updated_at = task.updated_at
    task.status = TaskStatus.IN_PROGRESS.value
    db.commit()
    db.refresh(task)

    # Verify status change and updated_at timestamp
    assert task.status == TaskStatus.IN_PROGRESS.value
    assert task.updated_at > original_updated_at

def test_task_comments(db: Session, test_user: User, test_project: Project):
    # Create a task
    task = Task(
        title="Comment Test Task",
        status=TaskStatus.TODO.value,
        priority=TaskPriority.LOW.value,
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
        status=TaskStatus.TODO.value,
        priority=TaskPriority.LOW.value,
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
    with pytest.raises(ValueError):  # Should raise a ValueError for invalid enum value
        task = Task(
            title="Invalid Status Task",
            status=TaskStatus("invalid_status"),  # Invalid status
            priority=TaskPriority.LOW,
            project_id=test_project.id,
            creator_id=test_user.id
        )
        db.add(task)
        db.commit()

    # Test invalid priority
    with pytest.raises(ValueError):  # Should raise a ValueError for invalid enum value
        task = Task(
            title="Invalid Priority Task",
            status=TaskStatus.TODO,
            priority=TaskPriority("invalid_priority"),  # Invalid priority
            project_id=test_project.id,
            creator_id=test_user.id
        )
        db.add(task)
        db.commit()

    # Test valid task creation
    task = Task(
        title="Valid Task",
        status=TaskStatus.TODO,
        priority=TaskPriority.LOW,
        project_id=test_project.id,
        creator_id=test_user.id
    )
    db.add(task)
    db.commit()
    assert task.id is not None

def test_cascade_delete(db: Session, test_user: User, test_project: Project):
    # Create a task with comments and time entries
    task = Task(
        title="Cascade Test Task",
        status=TaskStatus.TODO.value,
        priority=TaskPriority.LOW.value,
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

    # Delete task and verify cascade
    db.delete(task)
    db.commit()

    # Verify comment and time entry were deleted
    assert db.query(TaskComment).filter_by(task_id=task.id).first() is None
    assert db.query(TimeEntry).filter_by(task_id=task.id).first() is None 