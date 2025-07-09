from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import os
from dotenv import load_dotenv

load_dotenv()

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Email configuration
email_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "test@example.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "test_password"),
    MAIL_FROM=os.getenv("MAIL_FROM", "test@example.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "1025")),  # Default port for Python's SMTP debugging server
    MAIL_SERVER=os.getenv("MAIL_SERVER", "localhost"),  # Use local SMTP server for testing
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "SGE Dashboard"),
    MAIL_STARTTLS=False,  # Disable TLS for testing
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=False,  # Disable credentials for testing
    TEMPLATE_FOLDER=BASE_DIR / "templates" / "email"
)

# Initialize FastMail
fastmail = FastMail(email_conf)

# Initialize Jinja2 template environment
template_env = Environment(
    loader=FileSystemLoader(str(BASE_DIR / "templates" / "email"))
)

class EmailSchema(BaseModel):
    email: List[EmailStr]
    subject: str
    body: dict

async def send_task_assignment_email(email_to: List[EmailStr], task_title: str, task_description: str, assignee_name: str):
    """Send an email when a task is assigned to a user"""
    message = MessageSchema(
        subject=f"New Task Assignment: {task_title}",
        recipients=email_to,
        template_body={
            "task_title": task_title,
            "task_description": task_description,
            "assignee_name": assignee_name
        },
        subtype="html"
    )
    
    await fastmail.send_message(message, template_name="task_assigned.html")

async def send_task_update_email(email_to: List[EmailStr], task_title: str, update_type: str, updated_by: str):
    """Send an email when a task is updated"""
    message = MessageSchema(
        subject=f"Task Update: {task_title}",
        recipients=email_to,
        template_body={
            "task_title": task_title,
            "update_type": update_type,
            "updated_by": updated_by
        },
        subtype="html"
    )
    
    await fastmail.send_message(message, template_name="task_updated.html")

async def send_test_email(email_to: str) -> None:
    """
    Send a test email to verify the email configuration.
    
    Args:
        email_to: Email address to send the test to
    """
    test_task = {
        "title": "Test Task",
        "description": "This is a test task to verify email notifications.",
        "due_date": "2024-12-31",
        "assignee_name": "Test User",
        "task_url": "http://localhost:3000/tasks/1"
    }

    await send_task_assignment_email(
        email_to=[email_to],
        task_title=test_task["title"],
        task_description=test_task["description"],
        assignee_name=test_task["assignee_name"]
    ) 