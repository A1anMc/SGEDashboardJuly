import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.task_comment import TaskComment
from app.models.reaction import Reaction
from app.core.config import settings
from app.models.user import User
from app.models.task import Task

def test_create_comment(authorized_client: TestClient, db: Session, test_user, test_task):
    """Test creating a comment."""
    # Create comment data
    comment_data = {
        "content": "Test comment",
        "task_id": test_task.id,
        "mentions": []
    }
    
    # Create comment
    response = authorized_client.post(
        "/api/v1/comments/",
        json=comment_data
    )
    assert response.status_code == 200
    
    # Verify response
    data = response.json()
    assert data["content"] == comment_data["content"]
    assert data["task_id"] == comment_data["task_id"]
    assert data["user_id"] == test_user.id

def test_create_threaded_comment(authorized_client: TestClient, db: Session, test_user, test_task):
    """Test creating a threaded comment."""
    # Create parent comment
    parent_comment = TaskComment(
        content="Parent comment",
        task_id=test_task.id,
        user_id=test_user.id
    )
    db.add(parent_comment)
    db.commit()
    db.refresh(parent_comment)
    
    # Create threaded comment data
    comment_data = {
        "content": "Threaded comment",
        "task_id": test_task.id,
        "parent_id": parent_comment.id,
        "mentions": []
    }
    
    # Create threaded comment
    response = authorized_client.post(
        "/api/v1/comments/",
        json=comment_data
    )
    assert response.status_code == 200
    
    # Verify response
    data = response.json()
    assert data["content"] == comment_data["content"]
    assert data["task_id"] == comment_data["task_id"]
    assert data["parent_id"] == parent_comment.id
    assert data["user_id"] == test_user.id

def test_get_task_comments(authorized_client: TestClient, db: Session, test_user, test_task):
    """Test getting task comments."""
    # Create test comments
    comments = [
        TaskComment(
            content=f"Test comment {i}",
            task_id=test_task.id,
            user_id=test_user.id
        )
        for i in range(3)
    ]
    db.add_all(comments)
    db.commit()
    
    # Get comments
    response = authorized_client.get(
        f"/api/v1/comments/task/{test_task.id}/"
    )
    assert response.status_code == 200
    
    # Verify response
    data = response.json()
    assert len(data) == 3
    for i, comment in enumerate(data):
        assert comment["content"] == f"Test comment {i}"
        assert comment["task_id"] == test_task.id
        assert comment["user_id"] == test_user.id

def test_update_comment(authorized_client: TestClient, db: Session, test_user, test_task):
    """Test updating a comment."""
    # Create test comment
    comment = TaskComment(
        content="Original content",
        task_id=test_task.id,
        user_id=test_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Update comment data
    update_data = {
        "content": "Updated content",
        "mentions": []
    }
    
    # Update comment
    response = authorized_client.put(
        f"/api/v1/comments/{comment.id}/",
        json=update_data
    )
    assert response.status_code == 200
    
    # Verify response
    data = response.json()
    assert data["content"] == update_data["content"]
    assert data["task_id"] == test_task.id
    assert data["user_id"] == test_user.id

def test_delete_comment(authorized_client: TestClient, db: Session, test_user, test_task):
    """Test deleting a comment."""
    # Create test comment
    comment = TaskComment(
        content="Test comment",
        task_id=test_task.id,
        user_id=test_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Delete comment
    response = authorized_client.delete(
        f"/api/v1/comments/{comment.id}/"
    )
    assert response.status_code == 204
    
    # Verify comment is deleted
    deleted_comment = db.query(TaskComment).filter(TaskComment.id == comment.id).first()
    assert deleted_comment is None

def test_add_reaction(authorized_client: TestClient, db: Session, test_user, test_task):
    """Test adding a reaction to a comment."""
    # Create test comment
    comment = TaskComment(
        content="Test comment",
        task_id=test_task.id,
        user_id=test_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Add reaction
    emoji = "👍"
    response = authorized_client.post(
        f"/api/v1/comments/{comment.id}/reactions/{emoji}/"
    )
    assert response.status_code == 200
    
    # Verify reaction is added
    reaction = db.query(Reaction).filter(
        Reaction.comment_id == comment.id,
        Reaction.user_id == test_user.id
    ).first()
    assert reaction is not None
    assert reaction.emoji == "👍"

def test_remove_reaction(authorized_client: TestClient, db: Session, test_user, test_task):
    """Test removing a reaction from a comment."""
    # Create test comment
    comment = TaskComment(
        content="Test comment",
        task_id=test_task.id,
        user_id=test_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Add reaction
    reaction = Reaction(
        emoji="👍",
        comment_id=comment.id,
        user_id=test_user.id
    )
    db.add(reaction)
    db.commit()
    
    # Remove reaction
    response = authorized_client.delete(
        f"/api/v1/comments/{comment.id}/reactions/👍/"
    )
    assert response.status_code == 200
    
    # Verify reaction is removed
    deleted_reaction = db.query(Reaction).filter(
        Reaction.comment_id == comment.id,
        Reaction.user_id == test_user.id
    ).first()
    assert deleted_reaction is None

def test_multiple_reactions(authorized_client: TestClient, db: Session, test_user, test_task):
    """Test adding multiple reactions to a comment."""
    # Create test comment
    comment = TaskComment(
        content="Test comment",
        task_id=test_task.id,
        user_id=test_user.id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Add multiple reactions
    emojis = ["👍", "❤️", "😄"]
    for emoji in emojis:
        response = authorized_client.post(
            f"/api/v1/comments/{comment.id}/reactions/{emoji}/"
        )
        assert response.status_code == 200
    
    # Verify reactions are added
    reactions = db.query(Reaction).filter(
        Reaction.comment_id == comment.id,
        Reaction.user_id == test_user.id
    ).all()
    assert len(reactions) == len(emojis)
    reaction_emojis = [r.emoji for r in reactions]
    assert all(emoji in reaction_emojis for emoji in emojis) 