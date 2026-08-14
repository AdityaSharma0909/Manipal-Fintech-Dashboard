from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from onboarding_v2.constants import ApplicationStage, ApplicationStatus, LeadType, LendingPartner, ProductSubCategory
from onboarding_v2.models import (
    ApplicationV2,
    ApplicationStatusHistory,
    ApplicationStageSnapshot,
    LeadV2,
)
from onboarding_v2.helpers.stage_helpers import update_application_progress, save_stage_snapshot

User = get_user_model()


class TestApplicationTracing(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser_tracing", password="password")
        self.client.force_authenticate(user=self.user)

        self.lead = LeadV2.objects.create(
            customer_name="John Tracing",
            customer_id="CUST1234567",
            lead_code="LEAD1234567",
            contact_number="9876543210",
            product_category="GOLD_LOAN",
            product_subcategory=ProductSubCategory.GOLD_LOAN,
            lead_type=LeadType.FRESH,
            lending_partner=LendingPartner.AXIS_BANK,
        )
        self.application = ApplicationV2.objects.create(
            application_id="APP1234567",
            lead=self.lead,
            status=ApplicationStatus.DRAFT,
            stage=ApplicationStage.PAN,
        )

    def test_status_history_created_on_save_and_update(self):
        # Initial creation created status history
        history = ApplicationStatusHistory.objects.filter(application=self.application)
        self.assertEqual(history.count(), 1)
        self.assertIsNone(history.first().from_status)
        self.assertEqual(history.first().to_status, ApplicationStatus.DRAFT)

        # Update status
        self.application.status = ApplicationStatus.IN_PROGRESS
        self.application.save()

        history = ApplicationStatusHistory.objects.filter(application=self.application).order_by("created_at")
        self.assertEqual(history.count(), 2)
        latest = history.last()
        self.assertEqual(latest.from_status, ApplicationStatus.DRAFT)
        self.assertEqual(latest.to_status, ApplicationStatus.IN_PROGRESS)

    def test_stage_snapshot_sets_completed_at(self):
        self.assertIsNone(self.application.submitted_at)

        # Save stage snapshot with is_complete=True
        snap = save_stage_snapshot(self.application, ApplicationStage.PAN, {"pan": "ABCDE1234F"}, True, user=self.user)
        update_application_progress(self.application, ApplicationStage.PAN, True, {"pan": "ABCDE1234F"}, user=self.user)

        self.assertTrue(snap.is_complete)
        self.assertIsNotNone(snap.completed_at)

        # Now submit application
        submit_snap = save_stage_snapshot(self.application, ApplicationStage.SUBMITTED, {}, True, user=self.user)
        update_application_progress(self.application, ApplicationStage.SUBMITTED, True, {}, user=self.user)

        self.application.refresh_from_db()
        self.assertEqual(self.application.stage, ApplicationStage.SUBMITTED)
        self.assertEqual(self.application.status, ApplicationStatus.SENT_FOR_PRE_SCREENING)
        self.assertIsNotNone(self.application.submitted_at)
        self.assertIsNotNone(submit_snap.completed_at)

    def test_timeline_api(self):
        save_stage_snapshot(self.application, ApplicationStage.PAN, {"pan": "ABCDE1234F"}, True, user=self.user)
        response = self.client.get(f"/api/v2/onboarding/applications/{self.application.application_id}/timeline/")
        self.assertEqual(response.status_code, 200)
        res_data = response.json().get("data", {})
        self.assertEqual(res_data.get("application_id"), self.application.application_id)
        self.assertIn("status_history", res_data)
        self.assertIn("stage_snapshots", res_data)
        self.assertIsNotNone(res_data["stage_snapshots"][0]["completed_at"])
