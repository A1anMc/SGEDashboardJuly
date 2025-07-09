"""Test configuration module."""
import os

def setup_test_env():
    """Set up test environment variables."""
    os.environ.update({
        "TESTING": "true",
        "DATABASE_URL": "sqlite:///:memory:",
        "TEST_DATABASE_URL": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key",
        "JWT_SECRET_KEY": "test-jwt-key",
        "JWT_ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "SUPABASE_URL": "",
        "SUPABASE_KEY": "",
        "SUPABASE_SERVICE_ROLE_KEY": "",
        "SUPABASE_ANON_KEY": "",
        "SUPABASE_JWT_SECRET": "",
        # Email settings for testing
        "MAIL_USERNAME": "test@example.com",
        "MAIL_PASSWORD": "test_password",
        "MAIL_FROM": "test@example.com",
        "MAIL_PORT": "0",
        "MAIL_SERVER": "mock",
        "MAIL_FROM_NAME": "SGE Dashboard Test"
    }) 