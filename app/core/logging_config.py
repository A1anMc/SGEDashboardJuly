"""Enhanced logging configuration for the application."""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from app.core.config import settings

class StructuredLogger(logging.Logger):
    """Custom logger that outputs structured JSON logs in production."""
    
    def _log_to_json(self, level: int, msg: str, args: Any, exc_info: Any = None, extra: Dict = None) -> str:
        timestamp = datetime.utcnow().isoformat()
        log_data = {
            "timestamp": timestamp,
            "level": logging.getLevelName(level),
            "message": msg % args if args else msg,
            "environment": settings.ENV,
            "service": "navimpact-api"
        }
        
        if exc_info:
            if isinstance(exc_info, BaseException):
                log_data["error"] = str(exc_info)
            elif isinstance(exc_info, tuple):
                log_data["error"] = str(exc_info[1])
        
        if extra:
            log_data.update(extra)
            
        return json.dumps(log_data)

    def makeRecord(self, *args, **kwargs):
        record = super().makeRecord(*args, **kwargs)
        if settings.ENV == "production":
            record.msg = self._log_to_json(record.levelno, record.msg, record.args, 
                                         record.exc_info, record.extra if hasattr(record, 'extra') else None)
            record.args = ()
        return record

def setup_logging():
    """Configure application-wide logging with environment-specific settings."""
    # Register our custom logger
    logging.setLoggerClass(StructuredLogger)
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Clear any existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    if settings.ENV == "production":
        # Production format - JSON structured logging
        console_handler.setFormatter(logging.Formatter('%(message)s'))
    else:
        # Development format - human readable
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        console_handler.setFormatter(logging.Formatter(format_str))
    
    root_logger.addHandler(console_handler)
    
    # Set up specific loggers with appropriate levels
    loggers = {
        'app': settings.LOG_LEVEL,
        'uvicorn': logging.INFO,
        'alembic': logging.INFO,
        'sqlalchemy.engine': logging.WARNING,
        'sqlalchemy.pool': logging.WARNING,
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
    # Disable certain noisy loggers in production
    if settings.ENV == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        
    return root_logger

# Convenience functions for structured logging
def log_database_event(logger: logging.Logger, event_type: str, details: Dict[str, Any]):
    """Log database-related events with consistent structure."""
    logger.info("Database event", extra={
        "event_type": event_type,
        "database_details": details
    })

def log_api_event(logger: logging.Logger, endpoint: str, method: str, status_code: int, duration_ms: float):
    """Log API-related events with consistent structure."""
    logger.info("API request", extra={
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "duration_ms": duration_ms
    })

def log_error_event(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None):
    """Log error events with consistent structure and context."""
    error_details = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }
    logger.error("Application error", extra={"error_details": error_details}) 