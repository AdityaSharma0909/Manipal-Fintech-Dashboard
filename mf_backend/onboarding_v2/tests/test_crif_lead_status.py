from django.test import TestCase, override_settings

from crif_bureau.models import CrifBureauReportTrace
from onboarding_v2.views.leads import _resolve_crif_lead_eligibility


class CrifLeadEligibilityTests(TestCase):
    @override_settings(CRIF_BUREAU_ELIGIBLE_SCORE=600)
    def test_bureau_report_trace_is_used_for_lead_eligibility(self):
        trace = CrifBureauReportTrace.objects.create(
            phone_number="7001586476",
            score=720,
            status=CrifBureauReportTrace.FileDownloadStatus.COMPLETED,
        )

        result = _resolve_crif_lead_eligibility("+91 70015 86476")

        self.assertTrue(result["eligible"])
        self.assertEqual(result["score"], 720)
        self.assertEqual(result["trace_id"], trace.id)
