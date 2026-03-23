"""
Structured logging configuration using structlog
"""

import logging
import sys
from typing import Any
import json

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    structlog = None
    STRUCTLOG_AVAILABLE = False
from src.config import settings


class StdlibCompatLogger:
    """Compatibility logger that supports structlog-style keyword fields."""

    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def _log(self, level: int, event: str, **kwargs: Any) -> None:
        if kwargs:
            try:
                payload = json.dumps(kwargs, default=str)
            except Exception:
                payload = str(kwargs)
            self._logger.log(level, f"{event} {payload}")
        else:
            self._logger.log(level, event)

    def info(self, event: str, **kwargs: Any) -> None:
        self._log(logging.INFO, event, **kwargs)

    def warning(self, event: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, event, **kwargs)

    def debug(self, event: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, event, **kwargs)


def setup_logging() -> None:
    """Configure structured logging for the application"""

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )

    if not STRUCTLOG_AVAILABLE:
        logging.getLogger(__name__).warning("structlog_not_installed_using_stdlib")
        return

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.dev.ConsoleRenderer() if settings.app_env == "development"
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a structured logger instance"""
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    return StdlibCompatLogger(logging.getLogger(name))
