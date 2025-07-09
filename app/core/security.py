import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from urllib.parse import urlparse
import aiohttp
from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def verify_external_url(url: str) -> bool:
    """
    Verify if an external URL is allowed based on domain whitelist.
    Returns True if the domain is allowed, False otherwise.
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Remove 'www.' prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check if domain is in allowed list
        if domain not in settings.ALLOWED_EXTERNAL_DOMAINS:
            logger.warning(f"Attempted access to non-whitelisted domain: {domain}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying external URL {url}: {str(e)}")
        return False

async def verify_external_request(url: str, method: str = "GET", **kwargs) -> Optional[aiohttp.ClientResponse]:
    """
    Make a verified external request.
    Only proceeds if the domain is whitelisted.
    """
    if not await verify_external_url(url):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to this external domain is not allowed"
        )
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **kwargs) as response:
                return response
    except Exception as e:
        logger.error(f"Error making external request to {url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Error accessing external service"
        ) 