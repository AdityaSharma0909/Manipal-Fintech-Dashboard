"""
apps/utilities/retry_handler.py
==================================
Retry and backoff decorator utility using Tenacity.

Provides a pre-configured retry decorator for external API calls.
Used by: apps/integrations/icici/base_client.py

Retry strategy:
  - Exponential backoff with jitter
  - Configurable max retries, wait min/max
  - Retries only on transient errors (network, timeout, 5xx)
  - Raises IntegrationRetryExhaustedException after all attempts fail

Usage:
    from apps.utilities.retry_handler import with_retry

    @with_retry(max_attempts=3, wait_min=1, wait_max=8)
    def call_icici_api():
        ...

    # Or use default config (reads from settings.ICICI_CRM):
    @with_retry()
    def call_icici_api():
        ...
"""

import logging
from functools import wraps
from typing import Callable, Tuple, Type, Optional

import httpx
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError,
)
from django.conf import settings

from apps.common.exceptions.integration_exceptions import IntegrationRetryExhaustedException

logger = logging.getLogger(__name__)

# Exceptions that should trigger a retry
_RETRYABLE_EXCEPTIONS: Tuple[Type[Exception], ...] = (
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    httpx.ConnectError,
    httpx.TimeoutException,
    httpx.RemoteProtocolError,
)


def _get_icici_config() -> dict:
    return getattr(settings, "ICICI_CRM", {})


def with_retry(
    max_attempts: Optional[int] = None,
    wait_min: float = 1.0,
    wait_max: float = 10.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = _RETRYABLE_EXCEPTIONS,
) -> Callable:
    """
    Decorator factory that wraps a function with exponential backoff retry logic.

    Args:
        max_attempts     : Max number of total attempts (1 = no retry).
                           Defaults to settings.ICICI_CRM.MAX_RETRIES + 1.
        wait_min         : Minimum wait seconds between retries.
        wait_max         : Maximum wait seconds between retries.
        retryable_exceptions: Exception types that trigger a retry.

    Returns:
        Decorated function with retry logic applied.

    Raises:
        IntegrationRetryExhaustedException: After all retry attempts are exhausted.
    """
    cfg = _get_icici_config()
    resolved_attempts = max_attempts or (cfg.get("MAX_RETRIES", 3) + 1)
    backoff_factor = cfg.get("RETRY_BACKOFF_FACTOR", 0.5)

    def decorator(func: Callable) -> Callable:
        retrying = retry(
            stop=stop_after_attempt(resolved_attempts),
            wait=wait_exponential(
                multiplier=backoff_factor,
                min=wait_min,
                max=wait_max,
            ),
            retry=retry_if_exception_type(retryable_exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=False,
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return retrying(func)(*args, **kwargs)
            except RetryError as exc:
                logger.error(
                    "All %d retry attempts exhausted for %s. Last error: %s",
                    resolved_attempts,
                    func.__qualname__,
                    exc.last_attempt.exception(),
                )
                raise IntegrationRetryExhaustedException(
                    message=f"All retry attempts exhausted for {func.__qualname__}.",
                    details={"attempts": resolved_attempts},
                ) from exc

        return wrapper

    return decorator
