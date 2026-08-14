import requests
from celery.exceptions import Retry
from django.test import TestCase

from onboarding_v2.constants import ApplicationStatus
from onboarding_v2.models import ApplicationV2, LeadV2
from onboarding_v2.tasks import create_loan_task


class CreateLoanStatusTests(TestCase):
    def setUp(self):
        self.lead = LeadV2.objects.create(
            customer_id="CUST-1",
            contact_number="9000002222",
            customer_name="Loan User",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-CL-1",
            lead=self.lead,
        )

    def test_create_loan_sets_submitted_on_success(self):
        def fake_create_loan(_payload):
            return {"status": "SUCCESS"}

        with self._patch_create_loan(fake_create_loan):
            create_loan_task.run(self.app.application_id, {"k": "v"})

        self.app.refresh_from_db()
        self.lead.refresh_from_db()
        self.assertEqual(self.app.status, ApplicationStatus.SUBMITTED)
        self.assertEqual(self.lead.status, ApplicationStatus.SUBMITTED)

    def test_create_loan_sets_failed_on_http_error(self):
        resp = requests.Response()
        resp.status_code = 500
        resp._content = b'{"status":"SERVER_ERROR"}'
        http_err = requests.HTTPError(response=resp)

        def fake_create_loan(_payload):
            raise http_err

        with self._patch_create_loan(fake_create_loan):
            with self.assertRaises((requests.HTTPError, Retry)):
                create_loan_task.run(self.app.application_id, {"k": "v"})

        self.app.refresh_from_db()
        self.lead.refresh_from_db()
        self.assertEqual(self.app.status, ApplicationStatus.FAILED_TO_SUBMIT_CREATE_LOAN)
        self.assertEqual(self.lead.status, ApplicationStatus.FAILED_TO_SUBMIT_CREATE_LOAN)

    @staticmethod
    def _patch_create_loan(func):
        from unittest import mock

        return mock.patch("onboarding_v2.tasks.SaasClient.create_loan", side_effect=func)
