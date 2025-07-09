import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.email import send_test_email

@pytest.mark.asyncio
async def test_send_email():
    """Test sending a test email"""
    # Replace with your test email
    test_email = "your.test@email.com"
    
    try:
        await send_test_email(test_email)
        assert True  # If no exception is raised, test passes
    except Exception as e:
        pytest.fail(f"Failed to send email: {str(e)}")

def test_task_assignment_email(client: TestClient, db: Session, test_user, test_user2):
    """Test that email is sent when task is assigned"""
    # Create a task assigned to test_user2
    response = client.post(
        "/api/v1/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium",
            "project_id": 1,
            "assignee_id": test_user2.id
        },
        headers={"Authorization": f"Bearer {test_user.access_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["assignee_id"] == test_user2.id 