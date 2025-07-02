import logging
import logging.handlers
import os
from pathlib import Path

from app.core.config import settings

def setup_logging() -> logging.Logger:
    """
    Configure logging for the application.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("sge_dashboard")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # File handler (rotating log files)
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log startup message
    logger.info("Logging system initialized")
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    If no name is provided, returns the root logger.
    
    Args:
        name (str, optional): Logger name. Defaults to None.
    
    Returns:
        logging.Logger: Logger instance
    """
    if name:
        return logging.getLogger(f"sge_dashboard.{name}")
    return logging.getLogger("sge_dashboard") 