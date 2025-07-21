"""Logging configuration for MCP."""

import logging
import logging.config
import sys
from typing import Any, Dict

import structlog
from structlog.typing import Processor

from .settings import get_settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    settings = get_settings()
    
    # Configure standard library logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=False)
                if settings.log_format == "text"
                else structlog.processors.JSONRenderer(),
            },
        },
        "handlers": {
            "default": {
                "level": settings.log_level,
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": settings.log_level,
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
    
    # Add file handler if log file is specified
    if settings.log_file:
        logging_config["handlers"]["file"] = {
            "level": settings.log_level,
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": settings.log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
        for logger_name in logging_config["loggers"]:
            logging_config["loggers"][logger_name]["handlers"].append("file")
    
    logging.config.dictConfig(logging_config)
    
    # Configure structlog processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add different final processor based on format
    if settings.log_format == "json":
        processors.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)
    else:
        processors.extend([
            structlog.dev.ConsoleRenderer(colors=True),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Context managers for adding request context
class LoggingContext:
    """Context manager for adding structured logging context."""
    
    def __init__(self, **kwargs: Any):
        self.context = kwargs
    
    def __enter__(self) -> None:
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(**self.context)
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        structlog.contextvars.clear_contextvars()


def request_logging_context(
    request_id: str,
    method: str,
    path: str,
    user_id: str | None = None,
) -> LoggingContext:
    """Create logging context for HTTP requests."""
    context = {
        "request_id": request_id,
        "method": method,
        "path": path,
    }
    if user_id:
        context["user_id"] = user_id
    
    return LoggingContext(**context)


def agent_logging_context(
    agent_id: str,
    agent_type: str,
    task_id: str | None = None,
) -> LoggingContext:
    """Create logging context for agent operations."""
    context = {
        "agent_id": agent_id,
        "agent_type": agent_type,
    }
    if task_id:
        context["task_id"] = task_id
    
    return LoggingContext(**context) 