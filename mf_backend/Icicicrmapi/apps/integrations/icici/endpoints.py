"""
apps/integrations/icici/endpoints.py
======================================
ICICI CRM API endpoint URL registry.

All API endpoint path templates are defined here as string constants.
Concrete integration clients reference this registry — NO hardcoded paths
anywhere else in the codebase.

Naming convention:
  <RESOURCE>_<ACTION>
  e.g. CUSTOMER_GET_BY_ID, LEAD_CREATE, POLICY_LIST

Format notes:
  - Paths are relative to ICICI_CRM.BASE_URL (set in .env)
  - Use {placeholder} for path parameters — format() at call site
  - Group by logical domain using nested class

Usage (in concrete client):
    from apps.integrations.icici.endpoints import ICICIEndpoints
    path = ICICIEndpoints.Customer.GET_BY_ID.format(customer_id=cid)
    response = self._get(path)
"""


class ICICIEndpoints:
    """
    Registry of ICICI CRM API endpoint path templates.
    Extend each inner class.
    """

    # -------------------------------------------------------------------------
    # Authentication
    # -------------------------------------------------------------------------
    class Auth:
        TOKEN_GENERATE  = "/auth/token"
        TOKEN_REFRESH   = "/auth/token/refresh"
        TOKEN_REVOKE    = "/auth/token/revoke"

    # -------------------------------------------------------------------------
    # Customer
    # -------------------------------------------------------------------------
    class Customer:
        LIST            = "/customers"
        CREATE          = "/customers"
        GET_BY_ID       = "/customers/{customer_id}"
        UPDATE          = "/customers/{customer_id}"
        DELETE          = "/customers/{customer_id}"
        SEARCH          = "/customers/search"

    # -------------------------------------------------------------------------
    # Lead
    # -------------------------------------------------------------------------
    class Lead:
        LIST            = "/leads"
        CREATE          = "/leads"
        GET_BY_ID       = "/leads/{lead_id}"
        UPDATE          = "/leads/{lead_id}"
        ASSIGN          = "/leads/{lead_id}/assign"
        CONVERT         = "/leads/{lead_id}/convert"
        PUSH_LEAD       = "/push-lead"  # Typical ICICI CRM endpoint path

    # -------------------------------------------------------------------------
    # Policy
    # -------------------------------------------------------------------------
    class Policy:
        LIST            = "/policies"
        GET_BY_ID       = "/policies/{policy_id}"
        GET_BY_CUSTOMER = "/customers/{customer_id}/policies"
        RENEW           = "/policies/{policy_id}/renew"

    # -------------------------------------------------------------------------
    # Claim
    # -------------------------------------------------------------------------
    class Claim:
        LIST            = "/claims"
        CREATE          = "/claims"
        GET_BY_ID       = "/claims/{claim_id}"
        UPDATE_STATUS   = "/claims/{claim_id}/status"

    # -------------------------------------------------------------------------
    # Notification
    # -------------------------------------------------------------------------
    class Notification:
        SEND            = "/notifications/send"
        LIST            = "/notifications"
