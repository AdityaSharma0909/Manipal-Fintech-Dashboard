import json
import logging
import time
from typing import Any, Optional

try:
    import sentry_sdk
except ImportError:  # pragma: no cover - exercised only before dependency install
    sentry_sdk = None


logger = logging.getLogger("api.request")

REDACTED_KEYS = {
    "password",
    "token",
    "access",
    "refresh",
    "authorization",
    "secret",
    "otp",
    "pan",
    "aadhar",
}


def _set_sentry_tag(key: str, value: Any) -> None:
    if sentry_sdk is not None:
        sentry_sdk.set_tag(key, value)


def _set_sentry_context(name: str, value: dict[str, Any]) -> None:
    if sentry_sdk is not None:
        sentry_sdk.set_context(name, value)


def _set_sentry_user(value: Optional[dict[str, Any]]) -> None:
    if sentry_sdk is not None:
        sentry_sdk.set_user(value)


def _mask_value(key: str, value: Any) -> Any:
    if key.lower() in REDACTED_KEYS:
        return "[REDACTED]"
    return value


def _sanitize_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {key: _sanitize_payload(_mask_value(key, value)) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_sanitize_payload(item) for item in payload]
    return payload


class ApiLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._should_skip(request.path):
            return self.get_response(request)

        start_time = time.monotonic()
        request._api_log_start_time = start_time
        request_context = self._build_request_context(request)
        self._attach_sentry_context(request, request_context)

        logger.info(
            "API request started",
            extra={
                "method": request.method,
                "path": request.path,
                "query_params": request_context["query_params"],
                "user_id": request_context["user_id"],
            },
        )

        try:
            response = self.get_response(request)
        except Exception:
            duration_ms = round((time.monotonic() - start_time) * 1000, 2)
            logger.exception(
                "API request failed",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "duration_ms": duration_ms,
                    "user_id": request_context["user_id"],
                },
            )
            raise

        duration_ms = round((time.monotonic() - start_time) * 1000, 2)
        self._attach_response_context(response, duration_ms)
        level = logging.ERROR if response.status_code >= 500 else logging.INFO
        logger.log(
            level,
            "API request completed",
            extra={
                "method": request.method,
                "path": request.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "user_id": request_context["user_id"],
            },
        )
        return response

    def _attach_sentry_context(self, request, request_context: dict[str, Any]) -> None:
        _set_sentry_tag("api.path", request.path)
        _set_sentry_tag("api.method", request.method)
        _set_sentry_context("api_request", request_context)

        user = getattr(request, "user", None)
        if getattr(user, "is_authenticated", False):
            _set_sentry_user(
                {
                    "id": getattr(user, "pk", None),
                    "username": getattr(user, "username", None),
                    "email": getattr(user, "email", None),
                }
            )
        else:
            _set_sentry_user(None)

    def _attach_response_context(self, response, duration_ms: float) -> None:
        _set_sentry_context(
            "api_response",
            {
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        _set_sentry_tag("api.status_code", response.status_code)

    def _build_request_context(self, request) -> dict[str, Any]:
        return {
            "path": request.path,
            "method": request.method,
            "query_params": dict(request.GET.lists()),
            "content_type": request.content_type,
            "body": self._extract_body(request),
            "user_id": getattr(getattr(request, "user", None), "pk", None),
        }

    def _extract_body(self, request) -> Any:
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return None

        if request.content_type and "multipart/form-data" in request.content_type:
            return {"detail": "multipart payload omitted"}

        body = getattr(request, "body", b"")
        if not body:
            return None

        try:
            decoded_body = body.decode("utf-8")
        except UnicodeDecodeError:
            return {"detail": "non-text payload omitted"}

        if len(decoded_body) > 5000:
            return {"detail": "payload truncated", "size": len(decoded_body)}

        try:
            return _sanitize_payload(json.loads(decoded_body))
        except json.JSONDecodeError:
            return decoded_body[:1000]

    def _should_skip(self, path: str) -> bool:
        return path.startswith("/admin/") or path.startswith("/static/") or path.startswith("/media/")
