"""
apps/integrations/icici/base_client.py
========================================
ICICI CRM API base client.

Refactored to support fully dynamic configuration from PostgreSQL.
"""

import logging
from typing import Any, Dict, Optional

from django.conf import settings

from apps.utilities.http_client import HttpClient
from apps.utilities.retry_handler import with_retry

logger = logging.getLogger(__name__)


class ICICIBaseClient:
    """
    Base class for all ICICI CRM API integration clients.
    
    Initializes a shared HttpClient. Configuration can be passed at runtime
    (e.g. from DB) or fall back to settings.ICICI_CRM.
    """

    _SERVICE_NAME = "ICICI_CRM"

    def __init__(self, base_url: str = "", api_key: str = "", client_id: str = ""):
        cfg = getattr(settings, "ICICI_CRM", {})
        
        # Priority: Runtime Args > Settings
        actual_base_url = base_url or cfg.get("BASE_URL", "")
        actual_api_key = api_key or cfg.get("API_KEY", "")
        actual_client_id = client_id or cfg.get("CLIENT_ID", "")
        
        self._http = HttpClient(
            base_url=actual_base_url,
            timeout=cfg.get("TIMEOUT", 30),
            default_headers=self._build_default_headers(actual_api_key, actual_client_id),
            service_name=self._SERVICE_NAME,
        )
        logger.debug("ICICIBaseClient initialized.")

    @with_retry()
    def _get(self, path: str, params: Optional[Dict] = None, **kwargs):
        return self._http.get(path, params=params, **kwargs)

    @with_retry()
    def _post(self, path: str, payload: Optional[Dict] = None, **kwargs):
        return self._http.post(path, json=payload, **kwargs)

    @staticmethod
    def _build_default_headers(api_key: str, client_id: str) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if api_key:
            headers["apikey"] = api_key
        if client_id:
            headers["X-Client-ID"] = client_id
        return headers
