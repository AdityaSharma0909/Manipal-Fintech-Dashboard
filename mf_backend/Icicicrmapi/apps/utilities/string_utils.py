"""
apps/utilities/string_utils.py
================================
Common string manipulation helpers.

Centralises string cleaning, masking, and transformation logic
so business logic stays uncluttered.

Usage:
    from apps.utilities.string_utils import StringUtils
    masked = StringUtils.mask_pan("ABCDE1234F")        # "ABCDE****F"
    clean  = StringUtils.sanitize("  hello world  ")   # "hello world"
    snake  = StringUtils.to_snake_case("FirstName")    # "first_name"
"""

import re
import unicodedata
from typing import Optional


class StringUtils:

    @staticmethod
    def sanitize(value: Optional[str]) -> str:
        """Strip leading/trailing whitespace. Returns empty string for None."""
        if value is None:
            return ""
        return value.strip()

    @staticmethod
    def is_blank(value: Optional[str]) -> bool:
        """Return True if value is None, empty, or only whitespace."""
        return not value or not value.strip()

    @staticmethod
    def mask_pan(pan: Optional[str]) -> str:
        """
        Mask PAN card number for safe display/logging.
        e.g. "ABCDE1234F" → "ABCDE****F"
        """
        if not pan or len(pan) != 10:
            return "**********"
        return pan[:5] + "****" + pan[-1]

    @staticmethod
    def mask_mobile(mobile: Optional[str]) -> str:
        """
        Mask mobile number for safe display/logging.
        e.g. "9876543210" → "98XXXXXX10"
        """
        if not mobile or len(mobile) < 4:
            return "**masked**"
        return mobile[:2] + "X" * (len(mobile) - 4) + mobile[-2:]

    @staticmethod
    def mask_email(email: Optional[str]) -> str:
        """
        Mask email for safe display/logging.
        e.g. "john.doe@example.com" → "jo**@example.com"
        """
        if not email or "@" not in email:
            return "**@**.***"
        local, domain = email.split("@", 1)
        masked_local = local[:2] + "**" if len(local) > 2 else "**"
        return f"{masked_local}@{domain}"

    @staticmethod
    def to_snake_case(value: str) -> str:
        """Convert CamelCase or PascalCase to snake_case."""
        s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    @staticmethod
    def to_camel_case(value: str) -> str:
        """Convert snake_case to camelCase."""
        parts = value.split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])

    @staticmethod
    def truncate(value: str, max_length: int, suffix: str = "...") -> str:
        """Truncate a string to max_length, appending suffix if truncated."""
        if len(value) <= max_length:
            return value
        return value[: max_length - len(suffix)] + suffix

    @staticmethod
    def normalize_unicode(value: str) -> str:
        """Normalize Unicode characters to their closest ASCII equivalent."""
        return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")

    @staticmethod
    def remove_special_chars(value: str, allow_spaces: bool = True) -> str:
        """Remove all special characters; optionally preserve spaces."""
        pattern = r"[^a-zA-Z0-9 ]" if allow_spaces else r"[^a-zA-Z0-9]"
        return re.sub(pattern, "", value)
