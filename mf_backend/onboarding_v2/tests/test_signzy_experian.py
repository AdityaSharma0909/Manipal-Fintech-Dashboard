from unittest.mock import patch

from django.test import TestCase, override_settings

from onboarding_v2.constants import ApplicationStage, ApplicationStatus, BureauDecision
from onboarding_v2.models import ApplicationStageSnapshot, ApplicationV2, LeadV2
from onboarding_v2.signzy_experian import run_experian_bureau_check


class _MockResponse:
    text = '{"status": false, "message": "No Record Found"}'

    def json(self):
        return {"status": False, "message": "No Record Found"}


@override_settings(
    SIGNZY_EXP_AUTH_TOKEN="test-token",
    SIGNZY_CONSENT_MESSAGE_ID="consent-message",
)
class SignzyExperianNoRecordTests(TestCase):
    def setUp(self):
        self.lead = LeadV2.objects.create(
            customer_id="CUST-NO-REC",
            contact_number="8888888888",
            customer_name="Jane Smith",
            product_category="LOAN",
            pincode="560002",
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-NO-REC",
            lead=self.lead,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.PAN,
            payload={
                "pan_number": "ABCDE6789Z",
                "name_on_pan": "Jane Smith",
                "dob_as_per_pan": "1992-02-02",
                "contact_number": "8888888888",
            },
            is_complete=True,
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage=ApplicationStage.ADDRESS,
            payload={
                "permanent": {
                    "address_line1": "456 High St",
                    "pincode": "560002",
                    "state": "KA",
                    "city": "Bengaluru",
                },
                "current_same_as_permanent": True,
            },
            is_complete=True,
        )

    @patch("onboarding_v2.signzy_experian.requests.post", return_value=_MockResponse())
    def test_no_record_found_marks_application_eligible(self, _mock_post):
        response = run_experian_bureau_check(self.app)

        self.assertEqual(response.status_code, 200)
        self.app.refresh_from_db()
        self.assertEqual(self.app.bureau_decision, BureauDecision.APPROVED)
        self.assertEqual(self.app.status, ApplicationStatus.ELIGIBLE)
        self.assertIsNone(self.app.bureau_score)
        self.assertEqual(self.app.stage, ApplicationStage.ELIGIBILITY)
        self.assertEqual(self.app.stage_payload["eligibility"]["score_band"], "No Score")

    @patch("onboarding_v2.signzy_experian.requests.post", side_effect=Exception("network error"))
    def test_exception_marks_application_eligible(self, _mock_post):
        response = run_experian_bureau_check(self.app)

        self.assertEqual(response.status_code, 200)
        self.app.refresh_from_db()
        self.assertEqual(self.app.bureau_decision, BureauDecision.APPROVED)
        self.assertEqual(self.app.status, ApplicationStatus.ELIGIBLE)
        self.assertIsNone(self.app.bureau_score)
        self.assertEqual(self.app.stage, ApplicationStage.ELIGIBILITY)
        self.assertEqual(self.app.stage_payload["eligibility"]["score_band"], "No Score")
        self.assertEqual(self.app.bureau_raw["message"], "Experian bureau check failed")
