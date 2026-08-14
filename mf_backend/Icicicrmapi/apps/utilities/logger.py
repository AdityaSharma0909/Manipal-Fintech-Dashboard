"""
apps/utilities/logger.py
=========================
Centralised logging utilities.

Provides:
  - get_logger(name)    → returns a configured logger for any module
  - JsonFormatter       → structured JSON log formatter (used in production)
  - log_request(...)    → helper to log inbound HTTP request details
  - log_response(...)   → helper to log outbound HTTP response details
  - log_integration(...)→ helper to log ICICI external API calls

Usage:
    from apps.utilities.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Processing customer: %s", customer_id)
"""

import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger instance.
    The logger inherits handlers configured in settings.LOGGING.

    Args:
        name: Typically __name__ of the calling module.

    Returns:
        logging.Logger instance.
    """
    return logging.getLogger(name)


class JsonFormatter(logging.Formatter):
    """
    Structured JSON log formatter for production use.

    Each log line is a single-line JSON object containing:
      timestamp, level, logger, message, module, line, and optionally exc_info.

    Configured in settings.LOGGING["formatters"]["json"].
    """

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Attach correlation ID if present on the record
        if hasattr(record, "correlation_id"):
            log_entry["correlation_id"] = record.correlation_id

        # Attach exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info),
            }

        return json.dumps(log_entry, ensure_ascii=False)


# =============================================================================
# Contextual log helpers (used in middleware and integrations)
# =============================================================================

def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    correlation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    body: Optional[Dict] = None,
) -> None:
    """Log an inbound HTTP request."""
    logger.info(
        "Inbound request | method=%s | path=%s | correlation_id=%s | user=%s",
        method, path, correlation_id, user_id,
    )


def log_response(
    logger: logging.Logger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    correlation_id: Optional[str] = None,
) -> None:
    """Log an outbound HTTP response."""
    level = logging.WARNING if status_code >= 400 else logging.INFO
    logger.log(
        level,
        "Outbound response | method=%s | path=%s | status=%d | duration=%.2fms | correlation_id=%s",
        method, path, status_code, duration_ms, correlation_id,
    )


def log_integration_request(
    logger: logging.Logger,
    service: str,
    endpoint: str,
    method: str,
    correlation_id: Optional[str] = None,
) -> None:
    """Log an outgoing external API request (ICICI or other)."""
    logger.info(
        "Integration request | service=%s | method=%s | endpoint=%s | correlation_id=%s",
        service, method, endpoint, correlation_id,
    )


def log_integration_response(
    logger: logging.Logger,
    service: str,
    endpoint: str,
    status_code: int,
    duration_ms: float,
    correlation_id: Optional[str] = None,
) -> None:
    """Log an incoming response from an external API (ICICI or other)."""
    level = logging.WARNING if status_code >= 400 else logging.INFO
    logger.log(
        level,
        "Integration response | service=%s | endpoint=%s | status=%d | duration=%.2fms | correlation_id=%s",
        service, endpoint, status_code, duration_ms, correlation_id,
    )
