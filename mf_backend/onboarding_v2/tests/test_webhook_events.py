from unittest import mock

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from onboarding_v2.models import ApplicationV2, LeadV2, WebhookEvent
from onboarding_v2.constants import ApplicationStatus
from onboarding_v2.tasks import retry_failed_webhook_events
import requests
from onboarding_v2.tasks import submit_pre_screen_task, create_loan_task
from celery.exceptions import Retry


@override_settings(SAAS_WEBHOOK_SECRET="hook-secret")
class WebhookEventTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.lead = LeadV2.objects.create(
            customer_id="CUST1",
            contact_number="9000000000",
            customer_name="Test User",
        )
        self.application = ApplicationV2.objects.create(
            application_id="APP-1",
            lead=self.lead,
        )
        self.url = reverse("onboarding_v2_prescreen_webhook")

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    @mock.patch("onboarding_v2.views.run_bureau_check_task.delay")
    def test_webhook_creates_event_and_queues_bureau_check(self, mock_delay):
        payload = {
            "applicationId": self.application.application_id,
            "status": "ELIGIBLE",
            "request_id": "REQ-1",
        }
        resp = self.client.post(
            self.url,
            data=payload,
            format="json",
            HTTP_X_SAAS_TOKEN="hook-secret",
        )
        self.assertEqual(resp.status_code, 200)
        event = WebhookEvent.objects.get(application_id=self.application.application_id, request_id="REQ-1")
        self.assertEqual(event.status, WebhookEvent.Status.QUEUED)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, ApplicationStatus.READY_FOR_LOAN)
        self.assertEqual(self.application.saas_status, "ELIGIBLE")
        mock_delay.assert_called_once()
        args, _ = mock_delay.call_args
        self.assertEqual(args[0], self.application.application_id)
        self.assertEqual(args[1], str(event.id))

    def test_webhook_bad_token(self):
        with mock.patch("onboarding_v2.views.notify_saas_alert") as mock_alert:
            resp = self.client.post(
                self.url,
                data={"applicationId": self.application.application_id, "status": "ELIGIBLE"},
                format="json",
                HTTP_X_SAAS_TOKEN="wrong",
            )
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(WebhookEvent.objects.exists())
        mock_alert.assert_called_once()

    def test_webhook_not_eligible_marks_processed(self):
        payload = {
            "applicationId": self.application.application_id,
            "status": "NOT_ELIGIBLE",
            "request_id": "REQ-2",
        }
        resp = self.client.post(
            self.url,
            data=payload,
            format="json",
            HTTP_X_SAAS_TOKEN="hook-secret",
        )
        self.assertEqual(resp.status_code, 200)
        event = WebhookEvent.objects.get(request_id="REQ-2")
        self.assertEqual(event.status, WebhookEvent.Status.PROCESSED)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, ApplicationStatus.NOT_ELIGIBLE)
        self.assertEqual(self.application.saas_status, "NOT_ELIGIBLE")

    def test_webhook_esign_completed_saves_van_number(self):
        payload = {
            "applicationId": self.application.application_id,
            "status": "E-sign Completed",
            "request_id": None,
            "van_number": "SPFP052900104050",
            "remarks": "",
            "meta": {"source": "saas_tech_prescreening"},
            "esign_url": "",
        }
        resp = self.client.post(
            self.url,
            data=payload,
            format="json",
            HTTP_X_SAAS_TOKEN="hook-secret",
        )
        self.assertEqual(resp.status_code, 200)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, ApplicationStatus.ESIGN_COMPLETED)
        self.assertEqual(self.application.saas_status, "E-sign Completed")
        self.assertEqual(self.application.van_number, "SPFP052900104050")

    @mock.patch("onboarding_v2.tasks.run_bureau_check_task.delay")
    def test_retry_failed_webhook_events_requeues(self, mock_delay):
        event = WebhookEvent.objects.create(
            application_id=self.application.application_id,
            request_id="REQ-3",
            status=WebhookEvent.Status.FAILED,
            retry_count=1,
            next_retry_at=timezone.now() - timezone.timedelta(minutes=1),
        )
        result = retry_failed_webhook_events()
        self.assertEqual(result.get("enqueued"), 1)
        event.refresh_from_db()
        self.assertEqual(event.status, WebhookEvent.Status.QUEUED)
        self.assertIsNone(event.next_retry_at)
        mock_delay.assert_called_once_with(self.application.application_id, str(event.id))

    def test_webhook_fund_refund_completed(self):
        from onboarding_v2.constants import LeadType, ApplicationStage
        from onboarding_v2.models import ApplicationStageSnapshot
        
        self.application.loan_type = LeadType.BALANCE_TRANSFER
        self.application.status = ApplicationStatus.AMOUNT_NOT_PAID_TO_EXISTING_LENDER
        self.application.stage_payload = {
            "fund_refund": [
                {
                    "id": "1",
                    "amount": "100.00",
                    "transaction_reference_number": "TXN123",
                    "status": "UNVERIFIED",
                }
            ]
        }
        self.application.save()
        
        ApplicationStageSnapshot.objects.create(
            application=self.application,
            stage=ApplicationStage.LOAN,
            payload={"requested_amount": "100.00"},
            is_complete=True,
        )
        
        payload = {
            "applicationId": self.application.application_id,
            "transaction_reference_number": "TXN123",
            "status": "VERIFIED",
            "remarks": "verified by banker",
            "meta": {"source": "saas_tech_fund_refund"},
        }
        
        resp = self.client.post(
            self.url,
            data=payload,
            format="json",
            HTTP_X_SAAS_TOKEN="hook-secret",
        )
        
        self.assertEqual(resp.status_code, 200)
        self.application.refresh_from_db()
        
        refunds = self.application.stage_payload.get("fund_refund") or []
        self.assertEqual(len(refunds), 1)
        self.assertEqual(refunds[0]["status"], "VERIFIED")
        self.assertEqual(refunds[0]["remarks"], "verified by banker")
        
        self.assertEqual(
            self.application.status,
            ApplicationStatus.AMOUNT_NOT_PAID_TO_EXISTING_LENDER_BT_RETURN_COMPLETED
        )

    def test_webhook_fund_refund_syncs_with_snapshot(self):
        from onboarding_v2.constants import LeadType, ApplicationStage
        from onboarding_v2.models import ApplicationStageSnapshot

        self.application.loan_type = LeadType.BALANCE_TRANSFER
        self.application.stage_payload = {
            "fund_refund": [
                {
                    "id": "1",
                    "amount": "100.00",
                    "transaction_reference_number": "TXN123",
                    "status": "UNVERIFIED",
                }
            ]
        }
        self.application.save()

        # Create snapshot for FUND_REFUND in database
        snapshot = ApplicationStageSnapshot.objects.create(
            application=self.application,
            stage=ApplicationStage.FUND_REFUND,
            payload=[
                {
                    "id": "1",
                    "amount": "100.00",
                    "transaction_reference_number": "TXN123",
                    "status": "UNVERIFIED",
                }
            ],
            is_complete=True,
        )

        payload = {
            "applicationId": self.application.application_id,
            "transaction_reference_number": "TXN123",
            "status": "VERIFIED",
            "remarks": "verified by banker",
            "meta": {"source": "saas_tech_fund_refund"},
        }

        resp = self.client.post(
            self.url,
            data=payload,
            format="json",
            HTTP_X_SAAS_TOKEN="hook-secret",
        )

        self.assertEqual(resp.status_code, 200)
        self.application.refresh_from_db()
        snapshot.refresh_from_db()

        # Verify it updated stage_payload
        refunds_payload = self.application.stage_payload.get("fund_refund") or []
        self.assertEqual(refunds_payload[0]["status"], "VERIFIED")

        # Verify it also updated snapshot
        self.assertEqual(snapshot.payload[0]["status"], "VERIFIED")

    def test_webhook_fund_refund_fallback_to_snapshot(self):
        from onboarding_v2.constants import LeadType, ApplicationStage
        from onboarding_v2.models import ApplicationStageSnapshot

        self.application.loan_type = LeadType.BALANCE_TRANSFER
        # Empty stage_payload (or missing fund_refund)
        self.application.stage_payload = {}
        self.application.save()

        # Create snapshot containing the transaction
        snapshot = ApplicationStageSnapshot.objects.create(
            application=self.application,
            stage=ApplicationStage.FUND_REFUND,
            payload=[
                {
                    "id": "1",
                    "amount": "100.00",
                    "transaction_reference_number": "TXN_FALLBACK",
                    "status": "UNVERIFIED",
                }
            ],
            is_complete=True,
        )

        payload = {
            "applicationId": self.application.application_id,
            "transaction_reference_number": "TXN_FALLBACK",
            "status": "VERIFIED",
            "remarks": "verified via snapshot fallback",
            "meta": {"source": "saas_tech_fund_refund"},
        }

        resp = self.client.post(
            self.url,
            data=payload,
            format="json",
            HTTP_X_SAAS_TOKEN="hook-secret",
        )

        self.assertEqual(resp.status_code, 200)
        self.application.refresh_from_db()
        snapshot.refresh_from_db()

        # Check stage_payload is populated now and is marked VERIFIED
        refunds_payload = self.application.stage_payload.get("fund_refund") or []
        self.assertEqual(len(refunds_payload), 1)
        self.assertEqual(refunds_payload[0]["status"], "VERIFIED")

        # Check snapshot is also marked VERIFIED
        self.assertEqual(snapshot.payload[0]["status"], "VERIFIED")


class ApplicationErrorNotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.lead = LeadV2.objects.create(
            customer_id="CUST1",
            contact_number="9000000000",
            customer_name="Test User",
        )
        self.application = ApplicationV2.objects.create(
            application_id="APP-1",
            lead=self.lead,
        )

    @mock.patch("onboarding_v2.views.notify_app_step_error")
    @mock.patch("onboarding_v2.views.create_application")
    def test_app_create_error_notifies(self, mock_create, mock_notify):
        mock_create.side_effect = RuntimeError("db down")
        resp = self.client.post("/api/v2/onboarding/applications/", data={}, format="json")
        self.assertEqual(resp.status_code, 500)
        mock_notify.assert_called_once()


    @mock.patch("onboarding_v2.views.notify_app_step_error")
    @mock.patch("onboarding_v2.views.ApplicationStageSnapshot.objects.update_or_create")
    def test_stage_update_error_notifies(self, mock_update, mock_notify):
        mock_update.side_effect = RuntimeError("snapshot fail")
        payload = {
            "stage": "PAN",
            "is_complete": False,
            "payload": {
                "pan_number": "ABCDE1234F",
                "contact_number": "9000000000",
                "name_on_pan": "TEST",
                "dob_as_per_pan": "1990-01-01",
            },
        }
        resp = self.client.post(
            f"/api/v2/onboarding/applications/{self.application.application_id}/stage/",
            data=payload,
            format="json",
        )
        self.assertEqual(resp.status_code, 500)
        mock_notify.assert_called_once()

    @mock.patch("onboarding_v2.views.notify_app_step_error")
    @mock.patch("onboarding_v2.helpers.saas_helpers.build_pre_screen_payload")
    def test_submit_prescreen_error_notifies(self, mock_build, mock_notify):
        mock_build.side_effect = RuntimeError("payload build fail")
        resp = self.client.post(
            f"/api/v2/onboarding/applications/{self.application.application_id}/submit/",
            data={},
            format="json",
        )
        self.assertEqual(resp.status_code, 500)
        mock_notify.assert_called_once()

    @mock.patch("onboarding_v2.views.notify_app_step_error")
    @mock.patch("onboarding_v2.helpers.saas_helpers.build_create_loan_payload")
    def test_finalize_error_notifies(self, mock_build, mock_notify):
        mock_build.side_effect = RuntimeError("build fail")
        resp = self.client.post(
            f"/api/v2/onboarding/applications/{self.application.application_id}/finalize/",
            data={},
            format="json",
        )
        self.assertEqual(resp.status_code, 500)
        mock_notify.assert_called_once()

    @mock.patch("onboarding_v2.tasks.notify_saas_alert")
    @mock.patch("onboarding_v2.tasks.SaasClient.submit_pre_screen")
    def test_saas_prescreen_rejection_notifies(self, mock_submit, mock_alert):
        mock_submit.return_value = {"status": "REJECTED", "message": "bad data"}
        submit_pre_screen_task.run(self.application.application_id, {"k": "v"})
        mock_alert.assert_called_once()

    @mock.patch("onboarding_v2.tasks.notify_saas_alert")
    @mock.patch("onboarding_v2.tasks.SaasClient.create_loan")
    def test_saas_create_loan_rejection_notifies(self, mock_create, mock_alert):
        mock_create.return_value = {"status": "REJECTED", "message": "bad data"}
        create_loan_task.run(self.application.application_id, {"k": "v"})
        mock_alert.assert_called_once()


class PreScreenRequestIdTests(TestCase):
    def setUp(self):
        self.lead = LeadV2.objects.create(
            customer_id="CUST2",
            contact_number="9000000001",
            customer_name="Prescreen User",
        )
        self.application = ApplicationV2.objects.create(
            application_id="APP-PS-1",
            lead=self.lead,
        )

    @mock.patch("onboarding_v2.tasks.SaasClient.submit_pre_screen")
    def test_prescreen_sets_request_id_on_success(self, mock_submit):
        mock_submit.return_value = {"status": "SUCCESS"}
        submit_pre_screen_task.run(self.application.application_id, {"k": "v"})
        self.application.refresh_from_db()
        self.assertTrue(self.application.saas_request_id)

    @mock.patch("onboarding_v2.tasks.SaasClient.submit_pre_screen")
    def test_prescreen_does_not_set_request_id_on_http_error(self, mock_submit):
        response = requests.Response()
        response.status_code = 400
        response._content = b'{"status":"ERROR"}'
        http_error = requests.HTTPError(response=response)
        mock_submit.side_effect = http_error
        result = submit_pre_screen_task.run(self.application.application_id, {"k": "v"})
        self.assertEqual(result.get("status"), "FAILED")
        self.application.refresh_from_db()
        self.assertFalse(self.application.saas_request_id)

    @mock.patch("onboarding_v2.tasks.SaasClient.submit_pre_screen")
    def test_prescreen_retries_on_server_error(self, mock_submit):
        response = requests.Response()
        response.status_code = 500
        response._content = b'{"status":"ERROR"}'
        http_error = requests.HTTPError(response=response)
        mock_submit.side_effect = http_error
        with self.assertRaises(requests.HTTPError):
            submit_pre_screen_task.run(self.application.application_id, {"k": "v"})

    @mock.patch("onboarding_v2.tasks.SaasClient.create_loan")
    def test_create_loan_retries_on_server_error(self, mock_create):
        response = requests.Response()
        response.status_code = 503
        response._content = b'{"status":"ERROR"}'
        http_error = requests.HTTPError(response=response)
        mock_create.side_effect = http_error
        with self.assertRaises(requests.HTTPError):
            create_loan_task.run(self.application.application_id, {"k": "v"})
