from typing import Any

from utils.envSetup import environment

try:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
except ImportError:  # pragma: no cover - exercised only before dependency install
    sentry_sdk = None
    DjangoIntegration = None


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _as_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def init_sentry() -> None:
    if sentry_sdk is None:
        return

    dsn = environment.SENTRY_DSN
    if not dsn:
        return

    traces_sample_rate = _as_float(environment.SENTRY_TRACES_SAMPLE_RATE, default=0.0)
    profiles_sample_rate = _as_float(environment.SENTRY_PROFILES_SAMPLE_RATE, default=0.0)
    enable_logs = _as_bool(environment.SENTRY_ENABLE_LOGS, default=True)

    sentry_sdk.init(
        dsn=dsn,
        environment=environment.SENTRY_ENVIRONMENT or environment.APP_ENV or "development",
        release=environment.SENTRY_RELEASE or None,
        integrations=[DjangoIntegration()],
        send_default_pii=_as_bool(environment.SENTRY_SEND_DEFAULT_PII, default=True),
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        profiler_mode="thread",
        enable_tracing=traces_sample_rate > 0,
    )
