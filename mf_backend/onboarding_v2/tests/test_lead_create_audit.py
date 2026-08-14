from django.test import override_settings
from rest_framework.test import APIClient, APITestCase
from unittest.mock import patch

from crif_bureau.models import CrifBureauTrace
from onboarding_v2.constants import LeadStatus
from users.models import User
from onboarding_v2.models import LeadV2


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class LeadCreateAuditTests(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(username="agent-1", password="Pass@123")
        self.client.force_authenticate(user=self.user)

    def test_lead_create_sets_audit_fields(self) -> None:
        payload = {
            "contact_number": "9000011111",
            "customer_name": "Test User",
            "product_category": "LOAN",
            "product_subcategory": "GOLD_LOAN",
            "lead_type": "FRESH",
            "amount": "150000",
            "pincode": "560001",
            "source": "SELF",
        }

        resp = self.client.post("/api/v2/onboarding/leads/", data=payload, format="json")
        self.assertEqual(resp.status_code, 200)

        lead = LeadV2.objects.get(contact_number=payload["contact_number"])
        self.assertEqual(lead.created_by_id, self.user.pk)
        self.assertEqual(lead.modified_by_id, self.user.pk)
        self.assertEqual(lead.assigned_to_id, self.user.pk)

    @override_settings(CRIF_BUREAU_ELIGIBLE_SCORE=700)
    @patch("onboarding_v2.views.leads.sendToAxis")
    def test_lead_create_marks_not_eligible_from_low_crif_score(self, mock_send_to_axis) -> None:
        CrifBureauTrace.objects.create(
            phone_number="7523969888",
            score=650,
            status=CrifBureauTrace.Status.COMPLETED,
        )
        payload = {
            "contact_number": "7523969888",
            "customer_name": "Dipen Pau",
            "product_category": "LOAN",
            "product_subcategory": "GOLD_LOAN",
            "lead_type": "BANK_LEAD",
            "amount": "0",
            "pincode": "400055",
            "source": "SELF",
            "lending_partner": "Axis Bank",
            "bank": "Axis Bank",
            "bank_branch": "Vakola",
            "dob": "1996-05-23",
            "pan_number": "CTEPP4713L",
            "is_pan_verified": False,
        }

        resp = self.client.post("/api/v2/onboarding/leads/", data=payload, format="json")

        self.assertEqual(resp.status_code, 200)
        mock_send_to_axis.assert_not_called()
        lead = LeadV2.objects.get(contact_number=payload["contact_number"])
        self.assertEqual(lead.status, LeadStatus.NOT_ELIGIBLE)
        self.assertEqual(resp.json()["data"]["bureau_eligibility"]["score"], 650)
