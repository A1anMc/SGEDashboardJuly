"""Supabase client configuration and initialization."""

from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client() -> Client:
    """Initialize and return a Supabase client."""
    try:
        client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
        )
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to initialize Supabase client: {str(e)}")

def get_supabase_anon_client() -> Client:
    """Initialize and return an anonymous Supabase client."""
    try:
        client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_ANON_KEY
        )
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to initialize anonymous Supabase client: {str(e)}")

# Initialize clients
supabase = get_supabase_client()
supabase_anon = get_supabase_anon_client() 