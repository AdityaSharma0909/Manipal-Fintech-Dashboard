from unittest.mock import Mock, patch

from django.test import RequestFactory, TestCase, override_settings
from rest_framework.test import APIRequestFactory, force_authenticate

from crif_bureau.serializer import PhoneToPanSerializer
from crif_bureau.services import CrifBureauService
from crif_bureau.models import CrifBureauReportTrace
from crif_bureau.views.crif_report_view import crif_bureau_report
from crif_bureau.views.views import build_crif_callback_url, build_crif_redirect_url


class CrifCallbackUrlTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(CRIF_CALLBACK_URL="https://dev-api.radianfinserv.com/api/crif/webhook")
    def test_builds_path_style_callback_from_configured_webhook_url(self):
        request = self.factory.post("/api/crif/phone-to-pan/")

        callback_url = build_crif_callback_url(request, "7001586476")

        self.assertEqual(
            callback_url,
            "https://dev-api.radianfinserv.com/api/crif/webhook/7001586476/",
        )

    @override_settings(CRIF_CALLBACK_URL="https://dev-api.radianfinserv.com")
    def test_builds_native_webhook_path_from_production_host(self):
        request = self.factory.post("/api/crif/phone-to-pan/")

        callback_url = build_crif_callback_url(request, "7001586476")

        self.assertEqual(
            callback_url,
            "https://dev-api.radianfinserv.com/api/crif/webhook/7001586476/",
        )

    @override_settings(CRIF_CALLBACK_URL="https://relearn-unless-casino.ngrok-free.dev")
    def test_builds_webhook_path_when_only_host_is_configured(self):
        request = self.factory.post("/api/crif/phone-to-pan/")

        callback_url = build_crif_callback_url(request, "7001586476")

        self.assertEqual(
            callback_url,
            "https://relearn-unless-casino.ngrok-free.dev/api/crif/webhook/7001586476/",
        )

    @override_settings(CRIF_CALLBACK_URL="http://91.203.132.113/api/crif/webhook")
    def test_rejects_non_https_callback_url(self):
        request = self.factory.post("/api/crif/phone-to-pan/")

        with self.assertRaisesMessage(ValueError, "CRIF_CALLBACK_URL must use https"):
            build_crif_callback_url(request, "7001586476")

    @override_settings(CRIF_REDIRECT_URL="https://dev-api.radianfinserv.com/api/docs/")
    def test_accepts_native_https_redirect_url(self):
        self.assertEqual(
            build_crif_redirect_url(),
            "https://dev-api.radianfinserv.com/api/docs",
        )

    @override_settings(CRIF_REDIRECT_URL=None)
    def test_rejects_missing_redirect_url(self):
        with self.assertRaisesMessage(ValueError, "CRIF_REDIRECT_URL must be configured"):
            build_crif_redirect_url()


class CrifWebhookPayloadTests(TestCase):
    def test_extracts_signzy_response_data_payload(self):
        self.assertEqual(
            CrifBureauService.extract_request_data_from_payload({"responseData": "encrypted-response"}),
            "encrypted-response",
        )

    def test_extracts_nested_signzy_response_data_payload(self):
        self.assertEqual(
            CrifBureauService.extract_request_data_from_payload({"data": {"responseData": "encrypted-response"}}),
            "encrypted-response",
        )


class CrifErrorHandlingTests(TestCase):
    def test_phone_to_pan_serializer_rejects_invalid_phone_before_signzy_call(self):
        serializer = PhoneToPanSerializer(
            data={
                "phoneNumber": "855909984",
                "firstName": "Abhinav",
                "lastName": "Malhotra",
                "address": "Test address",
                "pincode": "110001",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(str(serializer.errors["phoneNumber"][0]), "Phone number must be exactly 10 digits")

    def test_phone_to_pan_view_rejects_invalid_phone_when_authenticated(self):
        class DummyUser:
            is_active = True
            is_authenticated = True
            role = "ADMIN"

        request = APIRequestFactory().post(
            "/api/crif/phone-to-pan/",
            {
                "phoneNumber": "855909984",
                "firstName": "Abhinav",
                "lastName": "Malhotra",
                "address": "Test address",
                "pincode": "110001",
            },
            format="json",
        )
        force_authenticate(request, user=DummyUser())

        from crif_bureau.views.views import PhoneToPanView

        response = PhoneToPanView.as_view()(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["success"], False)
        self.assertEqual(response.data["errors"], "Phone number must be exactly 10 digits")

    def test_signzy_validation_error_is_returned_as_bad_request(self):
        class DummyResponse:
            status_code = 400

        signzy_data = {
            "error": {
                "reason": "VALIDATION_ERROR",
                "status": 400,
                "message": "Phone number must be exactly 10 digits",
                "statusCode": 400,
            }
        }

        response = CrifBureauService.build_signzy_error_response(
            DummyResponse(),
            signzy_data,
            "Signzy phone_to_pan API returned an error",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["success"], False)
        self.assertEqual(response.data["error"], "Phone number must be exactly 10 digits")
        self.assertEqual(response.data["reason"], "VALIDATION_ERROR")


class CrifBureauReportPersistenceTests(TestCase):
    @patch("crif_bureau.views.crif_report_view.crif_report_request")
    def test_successful_report_persists_score_and_completed_status(self, report_request):
        report_request.return_value = Mock(
            status_code=200,
            json=Mock(return_value={
                "data": {
                    "crifPDF": "https://example.com/report.pdf",
                    "crifReport": {
                        "INDV-REPORT-FILE": {
                            "INDV-REPORTS": [{
                                "INDV-REPORT": {"SCORES": [{"SCORE-VALUE": "720"}]}
                            }]
                        }
                    },
                }
            }),
        )
        trace = CrifBureauReportTrace.objects.create(phone_number="7001586476")

        response = crif_bureau_report(trace, {"phoneNumber": trace.phone_number})

        trace.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])
        self.assertEqual(trace.score, 720)
        self.assertEqual(trace.status, CrifBureauReportTrace.FileDownloadStatus.COMPLETED)
