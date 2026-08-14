# apps.integrations.icici — ICICI CRM API integration package.
#
# All outbound calls to ICICI CRM APIs go through ICICIBaseClient.

from apps.integrations.icici.base_client import ICICIBaseClient
from apps.integrations.icici.lead_client import ICICILeadClient

__all__ = [
    "ICICIBaseClient",
    "ICICILeadClient",
]
