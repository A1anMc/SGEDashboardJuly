"""Centralized error handling for the FastAPI application."""

from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging
import time
import traceback
from datetime import datetime, timezone, timedelta
from collections import deque

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Error tracking with rolling window
class ErrorStats:
    def __init__(self, window_hours: int = 24):
        self.window_hours = window_hours
        self.errors = deque()  # [(timestamp, error_type), ...]
        self.last_cleanup = datetime.now(timezone.utc)
    
    def add_error(self, error_type: str) -> None:
        """Add an error to the tracking window."""
        current_time = datetime.now(timezone.utc)
        self.errors.append((current_time, error_type))
        self.cleanup_old_errors()
    
    def cleanup_old_errors(self) -> None:
        """Remove errors outside the rolling window."""
        current_time = datetime.now(timezone.utc)
        cutoff_time = current_time - timedelta(hours=self.window_hours)
        
        # Only cleanup if it's been at least 1 hour since last cleanup
        if (current_time - self.last_cleanup) < timedelta(hours=1):
            return
            
        while self.errors and self.errors[0][0] < cutoff_time:
            self.errors.popleft()
        
        self.last_cleanup = current_time
    
    @property
    def error_count_24h(self) -> int:
        """Get the number of errors in the last 24 hours."""
        self.cleanup_old_errors()
        return len(self.errors)
    
    @property
    def last_error_timestamp(self) -> Optional[datetime]:
        """Get the timestamp of the most recent error."""
        return self.errors[-1][0] if self.errors else None
    
    @property
    def last_error_type(self) -> Optional[str]:
        """Get the type of the most recent error."""
        return self.errors[-1][1] if self.errors else None
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of error statistics."""
        self.cleanup_old_errors()
        error_types = {}
        for _, error_type in self.errors:
            error_types[error_type] = error_types.get(error_type, 0) + 1
            
        return {
            "total_errors": len(self.errors),
            "error_types": error_types,
            "last_error": {
                "timestamp": self.last_error_timestamp,
                "type": self.last_error_type
            }
        }

# Initialize error stats
error_stats = ErrorStats()

def update_error_stats(error_type: str) -> None:
    """Update error statistics for monitoring."""
    error_stats.add_error(error_type)

def get_error_stats() -> Dict[str, Any]:
    """Get current error statistics."""
    return error_stats.get_error_summary()

def format_error_response(
    message: str,
    status_code: int,
    details: Optional[Any] = None,
    error_code: Optional[str] = None
) -> Dict[str, Any]:
    """Format standardized error response."""
    response = {
        "error": message,
        "status_code": status_code,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if details:
        response["details"] = details
    if error_code:
        response["error_code"] = error_code
        
    return response

def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI application."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """Handle request validation errors."""
        error_detail = []
        for error in exc.errors():
            error_entry = {
                "loc": " -> ".join(str(x) for x in error["loc"]),
                "msg": error["msg"],
                "type": error["type"]
            }
            error_detail.append(error_entry)
        
        logger.warning(
            "Validation error",
            extra={
                "request_id": request.state.request_id,
                "path": request.url.path,
                "method": request.method,
                "errors": error_detail
            }
        )
        
        update_error_stats("validation_error")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=format_error_response(
                message="Validation failed",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=error_detail,
                error_code="VALIDATION_ERROR"
            )
        )

    @app.exception_handler(SQLAlchemyError)
    async def db_exception_handler(
        request: Request,
        exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle database-related errors."""
        error_msg = "Database operation failed"
        error_code = "DATABASE_ERROR"
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Handle specific database errors
        if isinstance(exc, IntegrityError):
            if "unique constraint" in str(exc).lower():
                error_msg = "Resource already exists"
                error_code = "DUPLICATE_ERROR"
                status_code = status.HTTP_409_CONFLICT
            elif "foreign key constraint" in str(exc).lower():
                error_msg = "Referenced resource not found"
                error_code = "REFERENCE_ERROR"
                status_code = status.HTTP_400_BAD_REQUEST
        
        logger.error(
            f"Database error: {str(exc)}",
            extra={
                "request_id": request.state.request_id,
                "path": request.url.path,
                "method": request.method,
                "error_type": error_code
            },
            exc_info=True
        )
        
        update_error_stats("database_error")
        return JSONResponse(
            status_code=status_code,
            content=format_error_response(
                message=error_msg,
                status_code=status_code,
                error_code=error_code
            )
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request,
        exc: ValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        logger.warning(
            "Pydantic validation error",
            extra={
                "request_id": request.state.request_id,
                "path": request.url.path,
                "method": request.method,
                "errors": exc.errors()
            }
        )
        
        update_error_stats("pydantic_validation_error")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=format_error_response(
                message="Data validation failed",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=exc.errors(),
                error_code="PYDANTIC_VALIDATION_ERROR"
            )
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Handle any unhandled exceptions."""
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "request_id": request.state.request_id,
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        
        # Only show error details in development
        error_details = None
        if settings.DEBUG:
            error_details = {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback": traceback.format_exc().split("\n")
            }
        
        update_error_stats("unhandled_error")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=format_error_response(
                message="Internal server error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=error_details,
                error_code="INTERNAL_ERROR"
            )
        )

    # Add middleware to attach request ID
    @app.middleware("http")
    async def add_request_id(request: Request, call_next):
        request.state.request_id = str(time.time_ns())
        response = await call_next(request)
        return response 