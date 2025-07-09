from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.task_comment import TaskComment
from app.core.config import settings

def test_create_comment(client: TestClient, db: Session, test_user, test_task):
    """Test creating a new comment"""
    task_id = test_task.id
    user_id = test_user.id
    access_token = test_user.access_token
    
    response = client.post(
        f"{settings.API_V1_STR}/tasks/comments",
        json={
            "task_id": task_id,
            "content": "Test comment",
            "mentions": []
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Test comment"
    assert data["task_id"] == task_id
    assert data["user_id"] == user_id
    assert "created_at" in data
    assert "updated_at" in data

async def test_create_threaded_comment(test_task, test_user, db_session, client: TestClient):
    """Test creating a threaded comment"""
    task_id = test_task.id
    
    # Create parent comment
    parent_comment = TaskComment(
        task_id=task_id,
        user_id=test_user.id,
        content="Parent comment"
    )
    db_session.add(parent_comment)
    db_session.commit()
    
    parent_id = parent_comment.id
    
    # Create reply
    reply_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments",
        json={
            "task_id": task_id,
            "content": "Reply comment",
            "parent_id": parent_id,
            "mentions": []
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert reply_response.status_code == 200
    data = reply_response.json()
    assert data["content"] == "Reply comment"
    assert data["parent_id"] == parent_id

async def test_get_task_comments(test_task, test_user, db_session, client: TestClient):
    """Test getting all comments for a task"""
    task_id = test_task.id
    
    # Create parent comment
    parent_comment = TaskComment(
        task_id=task_id,
        user_id=test_user.id,
        content="Parent comment"
    )
    db_session.add(parent_comment)
    db_session.commit()
    
    parent_id = parent_comment.id
    
    # Create reply
    reply_comment = TaskComment(
        task_id=task_id,
        user_id=test_user.id,
        content="Reply comment",
        parent_id=parent_id
    )
    db_session.add(reply_comment)
    db_session.commit()
    
    # Get all comments
    response = client.get(
        f"{settings.API_V1_STR}/tasks/comments/task/{task_id}",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Both parent and reply comments
    parent_comment_data = next(c for c in data if c["parent_id"] is None)
    reply_comment_data = next(c for c in data if c["parent_id"] == parent_id)
    assert parent_comment_data["content"] == "Parent comment"
    assert reply_comment_data["content"] == "Reply comment"

async def test_update_comment(test_task, test_user, db_session, client: TestClient):
    """Test updating a comment"""
    task_id = test_task.id
    
    # Create comment
    comment = TaskComment(
        task_id=task_id,
        user_id=test_user.id,
        content="Original content"
    )
    db_session.add(comment)
    db_session.commit()
    
    comment_id = comment.id
    
    # Update comment
    update_response = client.put(
        f"{settings.API_V1_STR}/tasks/comments/{comment_id}",
        json={
            "content": "Updated content",
            "mentions": []
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["content"] == "Updated content"

async def test_delete_comment(test_task, test_user, db_session, client: TestClient):
    """Test deleting a comment"""
    task_id = test_task.id
    
    # Create comment
    comment = TaskComment(
        task_id=task_id,
        user_id=test_user.id,
        content="Test comment"
    )
    db_session.add(comment)
    db_session.commit()
    
    comment_id = comment.id
    
    # Delete comment
    delete_response = client.delete(
        f"{settings.API_V1_STR}/tasks/comments/{comment_id}",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert delete_response.status_code == 200
    
    # Verify comment is deleted
    comment = db_session.query(TaskComment).filter(TaskComment.id == comment_id).first()
    assert comment is None

def test_add_reaction(client: TestClient, db: Session, test_user, test_task):
    """Test adding a reaction to a comment"""
    task_id = test_task.id
    user_id = test_user.id
    
    # Create comment
    create_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments",
        json={
            "task_id": task_id,
            "content": "Comment with reaction",
            "mentions": []
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    comment_id = create_response.json()["id"]
    
    # Add reaction
    reaction_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments/{comment_id}/reactions/👍",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert reaction_response.status_code == 200
    data = reaction_response.json()
    assert "👍" in data
    assert user_id in data["👍"]

def test_remove_reaction(client: TestClient, db: Session, test_user):
    """Test removing a reaction from a comment"""
    # Create a task first
    task_response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium",
            "assignee_id": test_user.id
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert task_response.status_code == 200
    task_id = task_response.json()["id"]
    
    # Create a comment
    response = client.post(
        "/api/v1/tasks/comments",
        json={
            "content": "Test comment",
            "task_id": task_id
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == 200
    comment_id = response.json()["id"]
    
    # Add a reaction
    add_response = client.post(
        f"/api/v1/tasks/comments/{comment_id}/reactions/👍",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert add_response.status_code == 200
    assert "👍" in add_response.json()["reactions"]
    
    # Remove the reaction
    remove_response = client.delete(
        f"/api/v1/tasks/comments/{comment_id}/reactions/👍",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert remove_response.status_code == 200
    assert "👍" not in remove_response.json()["reactions"]

def test_multiple_reactions(client: TestClient, db: Session, test_user):
    """Test adding multiple reactions to a comment"""
    # Create a task first
    task_response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium",
            "assignee_id": test_user.id
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert task_response.status_code == 200
    task_id = task_response.json()["id"]
    
    # Create a comment
    response = client.post(
        "/api/v1/tasks/comments",
        json={
            "content": "Test comment",
            "task_id": task_id
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == 200
    comment_id = response.json()["id"]
    
    # Add first reaction
    response = client.post(
        f"/api/v1/tasks/comments/{comment_id}/reactions/👍",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == 200
    assert "👍" in response.json()["reactions"]
    
    # Add second reaction
    response = client.post(
        f"/api/v1/tasks/comments/{comment_id}/reactions/❤️",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    assert response.status_code == 200
    data = response.json()["reactions"]
    assert "👍" in data
    assert "❤️" in data 