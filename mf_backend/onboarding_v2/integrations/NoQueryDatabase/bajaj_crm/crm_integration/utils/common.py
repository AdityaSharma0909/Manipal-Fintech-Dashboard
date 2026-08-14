"""
utils/common.py
===============
Python equivalents of the C# Extensions.cs and CommonUtility helpers.

Covers:
  - JSON serialization helpers
  - Date parsing
  - HTML detection
  - Type-safe parsing helpers (ParseToInteger, ParseToText, ParseToBoolean)
"""

import re
import json
import hmac
import hashlib
import base64
import logging
from datetime import datetime
from typing import Optional, Any

logger = logging.getLogger(__name__)

# Pre-compiled regex matching C# HtmlRegex = @"<\/?[a-z][\s\S]*>"
_HTML_REGEX = re.compile(r"</?[a-zA-Z][\s\S]*>", re.IGNORECASE)


def is_html(text: str) -> bool:
    """Returns True if the string looks like HTML."""
    if not text or not text.strip():
        return False
    return bool(_HTML_REGEX.search(text))


def is_valid_json(text: str) -> bool:
    """Returns True if the string is valid JSON."""
    try:
        json.loads(text)
        return True
    except (ValueError, TypeError):
        return False


def to_json(obj: Any) -> str:
    """Serialises any object to a JSON string (indented)."""
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception as ex:
        logger.error(f"to_json failed: {ex}")
        return "{}"


def parse_to_integer(value: Any, default: int = 0) -> int:
    """Safe integer parser."""
    try:
        return int(str(value))
    except (ValueError, TypeError):
        return default


def parse_to_text(value: Any) -> str:
    """Safe string converter."""
    if value is None:
        return ""
    return str(value)


def parse_to_boolean(value: Any) -> bool:
    """Safe boolean parser."""
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in ("true", "1", "yes")


def parse_date_of_birth(dob: str) -> Optional[datetime]:
    """Parses a date-of-birth string in dd-MM-yyyy format."""
    if not dob:
        return None
    try:
        return datetime.strptime(dob, "%d-%m-%Y")
    except ValueError:
        logger.debug(f"ParseDateOfBirth failed for: {dob}")
        return None


def create_response(message: str, response_code: int, data: Any = None) -> dict:
    """Creates a standard API response dict."""
    return {
        "StatusCode": response_code,
        "StatusMessage": message,
        "Data": data,
    }


def create_error_response(message: str, status_code: int, data: Any = None) -> dict:
    """Creates a standard error response dict."""
    return create_response(message, status_code, data)


def create_success_response(message: str, status_code: int, data: Any = None) -> dict:
    """Creates a standard success response dict."""
    return create_response(message, status_code, data)


def read_http_status_string(status_code: int) -> str:
    """Returns the integer status code as string."""
    return str(status_code)
