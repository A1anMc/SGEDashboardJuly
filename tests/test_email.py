import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.email import send_test_email, send_task_assignment_email, fastmail
from app.core.security import create_access_token

@pytest.mark.asyncio
async def test_send_email():
    """Test sending a test email."""
    # Test email address
    test_email = "test@example.com"
    
    # Verify email configuration is in test mode
    assert fastmail.config.MAIL_SERVER == "mock"
    assert fastmail.config.SUPPRESS_SEND == True  # Use == for boolean comparison
    
    try:
        await send_test_email(test_email)
        assert True  # If no exception is raised, test passes
    except Exception as e:
        pytest.fail(f"Failed to send email: {str(e)}")

@pytest.mark.asyncio
async def test_task_assignment_email(client: TestClient, db: Session, test_user, test_user2):
    """Test sending a task assignment email."""
    # Test task data
    task_id = 1
    task_title = "Test Task"
    
    try:
        await send_task_assignment_email(task_id, test_user2.email, task_title)
        assert True  # If no exception is raised, test passes
    except Exception as e:
        pytest.fail(f"Failed to send task assignment email: {str(e)}") 