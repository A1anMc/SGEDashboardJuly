from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from datetime import datetime

from app.core.config import settings
from app.db.session import get_session_local, get_last_connection_error

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    """Get SQLAlchemy database session with enhanced error handling."""
    try:
        logger.info("Creating database session...")
        SessionLocal = get_session_local()
        logger.info("Session factory created successfully")
        
        db = SessionLocal()
        logger.info("Database session created successfully")
        
        # Test the connection
        try:
            logger.info("Testing database connection...")
            db.execute("SELECT 1")
            logger.info("Database connection test successful")
        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {str(e)}")
            conn_error = get_last_connection_error()
            if conn_error:
                raise HTTPException(
                    status_code=503,
                    detail={
                        "message": "Database connection error",
                        "error": str(conn_error.get("error")),
                        "last_attempt": datetime.fromtimestamp(conn_error.get("last_attempt", 0)).isoformat() if conn_error.get("last_attempt") else None,
                        "attempts": conn_error.get("attempts", 1)
                    }
                )
            raise HTTPException(
                status_code=503,
                detail=f"Database connection error: {str(e)}"
            )
        
        yield db
    except Exception as e:
        logger.error(f"Error creating database session: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Database service unavailable"
        )
    finally:
        try:
            db.close()
            logger.info("Database session closed successfully")
        except Exception as e:
            logger.warning(f"Error closing database session: {str(e)}")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """Get current authenticated user."""
    from app.models.user import User  # Import here to avoid circular import
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: Optional[int] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching user: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Database error while authenticating"
        )
    
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user

async def get_current_active_superuser(
    current_user = Depends(get_current_user),
):
    """Get current authenticated superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user 