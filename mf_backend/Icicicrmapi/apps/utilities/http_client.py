"""
apps/utilities/http_client.py
===============================
Configurable HTTP client wrapper around httpx.

Provides a pre-configured session-style client with:
  - Timeout enforcement
  - Automatic JSON handling
  - Correlation ID header injection
  - Request/response logging
  - Error normalization to integration exceptions
"""

import logging
import time
from typing import Any, Dict, Optional

import httpx
from django.conf import settings

from apps.common.exceptions.integration_exceptions import (
    ICICIAPIException,
    ICICITimeoutException,
    IntegrationException,
)
from apps.utilities.logger import log_integration_request, log_integration_response

logger = logging.getLogger(__name__)


class HttpClient:
    """
    Thin wrapper around httpx for outbound HTTP calls to external APIs.
    """

    def __init__(
        self,
        base_url: str = "",
        timeout: Optional[int] = None,
        default_headers: Optional[Dict[str, str]] = None,
        service_name: str = "EXTERNAL",
    ):
        icici_cfg = getattr(settings, "ICICI_CRM", {})
        self._base_url = base_url.rstrip("/") if base_url else ""
        self._timeout = timeout or icici_cfg.get("TIMEOUT", 30)
        self._service_name = service_name
        self._default_headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if default_headers:
            self._default_headers.update(default_headers)

    def get(self, path: str, params: Optional[Dict] = None, **kwargs) -> httpx.Response:
        return self._request("GET", path, params=params, **kwargs)

    def post(self, path: str, json: Optional[Dict] = None, **kwargs) -> httpx.Response:
        return self._request("POST", path, json=json, **kwargs)

    def _request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        correlation_id: Optional[str] = None,
        **kwargs,
    ) -> httpx.Response:
        # Dynamic URL detection: If path is absolute, use it directly.
        if path.startswith(("http://", "https://")):
            url = path
        else:
            url = f"{self._base_url}/{path.lstrip('/')}"

        merged_headers = dict(self._default_headers)
        if headers:
            merged_headers.update(headers)
        if correlation_id:
            merged_headers["X-Correlation-ID"] = correlation_id

        log_integration_request(
            logger=logger,
            service=self._service_name,
            endpoint=url,
            method=method,
            correlation_id=correlation_id,
        )

        start_time = time.monotonic()
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=merged_headers,
                    **kwargs,
                )

            duration_ms = (time.monotonic() - start_time) * 1000
            log_integration_response(
                logger=logger,
                service=self._service_name,
                endpoint=url,
                status_code=response.status_code,
                duration_ms=duration_ms,
                correlation_id=correlation_id,
            )

            self._raise_on_error(response, url)
            return response

        except httpx.TimeoutException as exc:
            raise ICICITimeoutException(
                message=f"Request to {self._service_name} timed out after {self._timeout}s.",
                details={"url": url, "method": method},
            ) from exc
        except httpx.RequestError as exc:
            raise IntegrationException(
                message=f"Network error contacting {self._service_name}.",
                details={"url": url, "error": str(exc)},
            ) from exc

    def _raise_on_error(self, response: httpx.Response, url: str) -> None:
        if response.is_success:
            return
        status_code = response.status_code
        try:
            body = response.json()
        except Exception:
            body = response.text
        
        # Mask secrets in logs if they appear in URL or body (basic implementation)
        clean_url = url.split("?")[0] # Hide query params
        
        if status_code in (401, 403):
            from apps.common.exceptions.integration_exceptions import ICICIAuthException
            raise ICICIAuthException(
                message=f"{self._service_name} rejected authentication.",
                details={"status": status_code, "body": "Masked for security"},
            )
        
        raise ICICIAPIException(
            message=f"{self._service_name} returned error {status_code}.",
            details={"status": status_code, "url": clean_url},
        )
