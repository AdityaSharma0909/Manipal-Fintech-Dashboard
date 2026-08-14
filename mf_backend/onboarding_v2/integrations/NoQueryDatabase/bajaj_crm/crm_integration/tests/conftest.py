"""
tests/conftest.py
=================
Shared pytest fixtures for unit and integration tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from django.test import RequestFactory
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """DRF test API client (unauthenticated by default)."""
    return APIClient()


@pytest.fixture
def auth_api_client(api_client):
    """DRF test API client with a fake Bearer token pre-set."""
    api_client.credentials(HTTP_AUTHORIZATION="Bearer fake-test-token")
    return api_client


@pytest.fixture
def request_factory():
    """Django RequestFactory for constructing raw request objects."""
    return RequestFactory()


@pytest.fixture
def mock_user():
    """Mock authenticated user injected by the custom auth backend."""
    user = MagicMock()
    user.id = 110252
    user.username = "110252"
    user.roles = ["SBO"]
    user.is_authenticated = True
    return user


@pytest.fixture
def valid_lead_payload():
    """Standard valid lead creation payload."""
    return {
        "FullName": "Ravi Sharma",
        "MobileNo": "9876543210",
        "LoanAmount": 50000,
        "SBOState": "Maharashtra",
        "SBODistrict": "Pune",
        "Branch": "PUNE001",
    }


@pytest.fixture
def sample_bajaj_api_response():
    """Simulated Bajaj CRM raw decrypted JSON response for success case."""
    return {
        "status": "success",
        "statusCode": 200,
        "message": "Lead Created Successfully",
        "data": {
            "remarks": "Lead accepted",
            "lead_id": 987654,
            "status": "New",
            "loan_officier_id": "LO001",
            "loan_officer_mobile": "9999999999",
            "loan_officier_name": "Loan Officer",
            "branch": "PUNE001",
            "customer_type": "Individual",
        },
    }


@pytest.fixture
def sample_branch_db_row():
    """Simulated DB response from branch lookup."""
    return {
        "ResponseCode": 200,
        "ResponseMessage": "Success",
        "Pincode": "411001",
        "BranchCode": "PUNE001",
    }
