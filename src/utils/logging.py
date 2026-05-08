"""
Structured logging configuration using structlog
Production-grade structured logging with request context
"""

import logging
import sys
import structlog

from src.config import settings


def setup_logging(log_level: str | None = None) -> None:
    """
    Configure production-grade structured logging
    
    Features:
    - Structured output (JSON in production, pretty in dev)
    - Request ID context propagation
    - Automatic timestamp in ISO format
    - Exception info included
    - Environment-aware formatting
    """
    level = log_level or settings.log_level.upper()

    # Configure standard library logging first
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level),
    )

    # Configure structlog processors based on environment
    is_dev = settings.app_env == "development"
    
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer() if is_dev else structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance with optional context binding"""
    return structlog.get_logger(name)
