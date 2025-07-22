from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import os
from dotenv import load_dotenv
from app.core.config import settings

load_dotenv()

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Email configuration
def get_email_config():
    """Get email configuration based on environment"""
    if settings.TESTING:
        # Mock email configuration for testing
        return ConnectionConfig(
            MAIL_USERNAME="test@example.com",
            MAIL_PASSWORD="test_password",
            MAIL_FROM="test@example.com",
            MAIL_PORT=0,  # Use port 0 to indicate mock server
            MAIL_SERVER="mock",  # Use mock server for testing
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=False,
            SUPPRESS_SEND=True,  # Don't actually send emails in tests
            USE_CREDENTIALS=False,
            TEMPLATE_FOLDER=str(BASE_DIR / "templates" / "email")
        )
    else:
        # Production email configuration
        return ConnectionConfig(
            MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
            MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
            MAIL_FROM=os.getenv("MAIL_FROM"),
            MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
            MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            TEMPLATE_FOLDER=str(BASE_DIR / "templates" / "email")
        )

# Create FastMail instance
fastmail = FastMail(get_email_config())

# Load email templates
template_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates" / "email"))
)

async def send_test_email(email: str) -> None:
    """Send a test email."""
    message = MessageSchema(
        subject="Test Email",
        recipients=[email],
        body="This is a test email from the NavImpact Dashboard.",
        subtype="html"
    )
    await fastmail.send_message(message)

async def send_task_assignment_email(task_id: int, assignee_email: str, task_title: str) -> None:
    """Send an email when a task is assigned to a user."""
    message = MessageSchema(
        subject=f"Task Assignment: {task_title}",
        recipients=[assignee_email],
        body=f"""
        <h2>Task Assignment</h2>
        <p>You have been assigned to task #{task_id}: {task_title}</p>
        <p>Please log in to the dashboard to view the task details.</p>
        """,
        subtype="html"
    )
    await fastmail.send_message(message) 