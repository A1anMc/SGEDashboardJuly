"""Logging configuration for the application."""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
import json
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

class RequestContextFilter(logging.Filter):
    """Add request context to log records."""
    
    def filter(self, record):
        # These attributes will be empty if there's no request context
        record.request_id = getattr(record, "request_id", "no_request")
        record.path = getattr(record, "path", "no_path")
        record.method = getattr(record, "method", "no_method")
        record.user_id = getattr(record, "user_id", "no_user")
        record.ip = getattr(record, "ip", "no_ip")
        return True

class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "request_id": getattr(record, "request_id", "no_request"),
            "path": getattr(record, "path", "no_path"),
            "method": getattr(record, "method", "no_method"),
            "user_id": getattr(record, "user_id", "no_user"),
            "ip": getattr(record, "ip", "no_ip")
        }
        
        # Add extra fields if they exist
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": str(record.exc_info[0].__name__),
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        return json.dumps(log_data)

def setup_logging(log_level: Optional[str] = None) -> None:
    """Configure application-wide logging."""
    
    # Use provided log level or default from settings
    log_level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatters
    json_formatter = JSONFormatter()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    # 1. Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    
    # 2. JSON file handler with rotation
    json_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "app.json",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    json_handler.setFormatter(json_formatter)
    
    # 3. Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        LOGS_DIR / "error.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Add request context filter
    context_filter = RequestContextFilter()
    root_logger.addFilter(context_filter)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(json_handler)
    root_logger.addHandler(error_handler)
    
    # Configure Sentry integration if DSN is provided
    if settings.SENTRY_DSN:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            integrations=[
                sentry_logging,
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ]
        )
        
        logging.info("Sentry integration initialized")
    
    # Log startup message
    logging.info(
        "Logging system initialized",
        extra={
            "log_level": log_level,
            "handlers": ["console", "json_file", "error_file"],
            "sentry_enabled": bool(settings.SENTRY_DSN)
        }
    ) 