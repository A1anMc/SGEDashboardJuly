import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.task import Task, TaskComment
from app.models.user import User
from app.core.deps import get_db
from app.main import app
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

def test_create_threaded_comment(client: TestClient, db: Session, test_user, test_task):
    """Test creating a threaded comment"""
    task_id = test_task.id
    user_id = test_user.id
    
    # Create parent comment
    parent_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments",
        json={
            "task_id": task_id,
            "content": "Parent comment",
            "mentions": []
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    parent_id = parent_response.json()["id"]
    
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

def test_get_task_comments(client: TestClient, db: Session, test_user, test_task):
    """Test getting all comments for a task"""
    task_id = test_task.id
    user_id = test_user.id
    
    # Create parent comment
    parent_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments",
        json={
            "task_id": task_id,
            "content": "Parent comment",
            "mentions": []
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    parent_id = parent_response.json()["id"]
    
    # Create reply
    client.post(
        f"{settings.API_V1_STR}/tasks/comments",
        json={
            "task_id": task_id,
            "content": "Reply comment",
            "parent_id": parent_id,
            "mentions": []
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    # Get all comments
    response = client.get(
        f"{settings.API_V1_STR}/tasks/comments/task/{task_id}",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # One parent comment
    assert len(data[0]["replies"]) == 1  # One reply

def test_update_comment(client: TestClient, db: Session, test_user, test_task):
    """Test updating a comment"""
    task_id = test_task.id
    user_id = test_user.id
    
    # Create comment
    create_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments",
        json={
            "task_id": task_id,
            "content": "Original content",
            "mentions": []
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    comment_id = create_response.json()["id"]
    
    # Update comment
    update_response = client.put(
        f"{settings.API_V1_STR}/tasks/comments/{comment_id}",
        json={
            "content": "Updated content"
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["content"] == "Updated content"

def test_delete_comment(client: TestClient, db: Session, test_user, test_task):
    """Test deleting a comment"""
    task_id = test_task.id
    user_id = test_user.id
    
    # Create comment
    create_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments",
        json={
            "task_id": task_id,
            "content": "Comment to delete",
            "mentions": []
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    comment_id = create_response.json()["id"]
    
    # Delete comment
    delete_response = client.delete(
        f"{settings.API_V1_STR}/tasks/comments/{comment_id}",
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert delete_response.status_code == 200
    
    # Verify comment is deleted
    comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
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
        f"{settings.API_V1_STR}/tasks/comments/{comment_id}/reaction",
        json={
            "emoji": "👍",
            "action": "add"
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert reaction_response.status_code == 200
    data = reaction_response.json()
    assert "👍" in data["reactions"]
    assert user_id in data["reactions"]["👍"]

def test_remove_reaction(client: TestClient, db: Session, test_user, test_task):
    """Test removing a reaction from a comment"""
    task_id = test_task.id
    user_id = test_user.id
    access_token = test_user.access_token
    
    # Create comment
    create_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments",
        json={
            "task_id": task_id,
            "content": "Comment with reaction",
            "mentions": []
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    comment_id = create_response.json()["id"]
    
    # Add reaction
    add_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments/{comment_id}/reaction",
        json={
            "emoji": "👍",
            "action": "add"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert add_response.status_code == 200
    assert "👍" in add_response.json()["reactions"]
    assert user_id in add_response.json()["reactions"]["👍"]
    
    # Remove reaction
    remove_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments/{comment_id}/reaction",
        json={
            "emoji": "👍",
            "action": "remove"
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert remove_response.status_code == 200
    assert "👍" not in remove_response.json()["reactions"]
    
    # Verify the reactions field is an empty dict, not None
    comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    assert comment.reactions == {}

def test_multiple_reactions(client: TestClient, db: Session, test_user, test_task):
    """Test handling multiple reactions on a comment"""
    task_id = test_task.id
    user_id = test_user.id
    access_token = test_user.access_token
    
    # Create comment
    create_response = client.post(
        f"{settings.API_V1_STR}/tasks/comments",
        json={
            "task_id": task_id,
            "content": "Comment with multiple reactions",
            "mentions": []
        },
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    comment_id = create_response.json()["id"]
    
    # Add multiple reactions
    reactions = ["👍", "❤️", "🎉"]
    for emoji in reactions:
        response = client.post(
            f"{settings.API_V1_STR}/tasks/comments/{comment_id}/reaction",
            json={
                "emoji": emoji,
                "action": "add"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert emoji in response.json()["reactions"]
    
    # Remove reactions one by one
    for emoji in reactions:
        response = client.post(
            f"{settings.API_V1_STR}/tasks/comments/{comment_id}/reaction",
            json={
                "emoji": emoji,
                "action": "remove"
            },
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200
        assert emoji not in response.json()["reactions"]
    
    # Verify all reactions are removed
    comment = db.query(TaskComment).filter(TaskComment.id == comment_id).first()
    assert comment.reactions == {} 