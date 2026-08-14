"""
apps/utilities/date_utils.py
==============================
Date and datetime utility helpers.

Centralises all date parsing, formatting, and timezone conversion.
Always work in UTC internally; convert to IST only for display.

Usage:
    from apps.utilities.date_utils import DateUtils
    now_utc  = DateUtils.now_utc()
    now_ist  = DateUtils.now_ist()
    fmt      = DateUtils.format_datetime(now_utc)
    parsed   = DateUtils.parse_date("2024-01-31")
"""

from datetime import datetime, date, timezone, timedelta
from typing import Optional
import pytz

IST = pytz.timezone("Asia/Kolkata")
UTC = timezone.utc

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
DISPLAY_FORMAT = "%d %b %Y, %I:%M %p"


class DateUtils:

    @staticmethod
    def now_utc() -> datetime:
        """Return current UTC datetime (timezone-aware)."""
        return datetime.now(tz=UTC)

    @staticmethod
    def now_ist() -> datetime:
        """Return current IST datetime (timezone-aware)."""
        return datetime.now(tz=IST)

    @staticmethod
    def to_ist(dt: datetime) -> datetime:
        """Convert any timezone-aware datetime to IST."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.astimezone(IST)

    @staticmethod
    def to_utc(dt: datetime) -> datetime:
        """Convert any timezone-aware datetime to UTC."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=IST)
        return dt.astimezone(UTC)

    @staticmethod
    def format_datetime(dt: datetime, fmt: str = DATETIME_FORMAT) -> str:
        """Format a datetime object to ISO string."""
        return dt.strftime(fmt)

    @staticmethod
    def format_date(d: date, fmt: str = DATE_FORMAT) -> str:
        """Format a date object to string."""
        return d.strftime(fmt)

    @staticmethod
    def parse_datetime(value: str, fmt: str = DATETIME_FORMAT) -> datetime:
        """
        Parse a datetime string.

        Returns:
            Parsed datetime (naive — caller should localize as needed).

        Raises:
            ValueError: If the string doesn't match the format.
        """
        return datetime.strptime(value, fmt)

    @staticmethod
    def parse_date(value: str, fmt: str = DATE_FORMAT) -> date:
        """Parse a date string."""
        return datetime.strptime(value, fmt).date()

    @staticmethod
    def days_between(start: date, end: date) -> int:
        """Return number of days between two dates."""
        return (end - start).days

    @staticmethod
    def add_days(dt: datetime, days: int) -> datetime:
        """Add N days to a datetime."""
        return dt + timedelta(days=days)

    @staticmethod
    def is_past(dt: datetime) -> bool:
        """Check if a datetime is in the past (relative to UTC now)."""
        now = DateUtils.now_utc()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt < now

    @staticmethod
    def is_future(dt: datetime) -> bool:
        """Check if a datetime is in the future."""
        return not DateUtils.is_past(dt)
