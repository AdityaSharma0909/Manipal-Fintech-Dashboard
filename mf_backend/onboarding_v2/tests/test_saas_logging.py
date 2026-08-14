from django.test import TestCase

from onboarding_v2.loggers import log_saas_request
from onboarding_v2.models import ApplicationV2, LeadV2, SaasRequestLog


class SaasRequestLogTests(TestCase):
    def setUp(self):
        self.lead = LeadV2.objects.create(
            customer_id="CUST-1",
            contact_number="9000011111",
            customer_name="Test User",
        )
        self.application = ApplicationV2.objects.create(
            application_id="APP-1",
            lead=self.lead,
        )

    def test_attempt_and_response_updates_same_row(self):
        log_saas_request(
            application=self.application,
            request_type=SaasRequestLog.RequestType.CREATE_LOAN,
            payload={"foo": "bar"},
            increment_attempt=True,
        )
        log = SaasRequestLog.objects.get(
            application_identifier=self.application.application_id,
            request_type=SaasRequestLog.RequestType.CREATE_LOAN,
        )
        self.assertEqual(log.attempts, 1)
        self.assertEqual(log.last_payload, {"foo": "bar"})
        self.assertIsNotNone(log.first_attempt_at)
        self.assertIsNotNone(log.last_attempt_at)

        log_saas_request(
            application=self.application,
            request_type=SaasRequestLog.RequestType.CREATE_LOAN,
            response_status=200,
            response_body={"ok": True},
        )
        log.refresh_from_db()
        self.assertEqual(log.attempts, 1)  # no extra attempt counted
        self.assertEqual(log.last_response_status, 200)
        self.assertEqual(log.last_response_body, {"ok": True})
        self.assertIsNone(log.last_error)

    def test_error_logs_without_increment(self):
        log_saas_request(
            application=self.application,
            request_type=SaasRequestLog.RequestType.BUREAU_CHECK,
            error="boom",
        )
        log = SaasRequestLog.objects.get(
            application_identifier=self.application.application_id,
            request_type=SaasRequestLog.RequestType.BUREAU_CHECK,
        )
        self.assertEqual(log.attempts, 0)
        self.assertEqual(log.last_error, "boom")
