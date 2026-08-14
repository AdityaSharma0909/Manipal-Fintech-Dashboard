from requests import RequestException, Timeout
from rest_framework import status
from rest_framework.response import Response

from crif_bureau.serializer import SendCrifRequestSerializer
from crif_bureau.services.signzy_service import decrypt_data, phone_to_pan


class CrifBureauService:

    @staticmethod
    def json_or_text(response):
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text}

    @staticmethod
    def extract_request_data_from_payload(payload):
        if not isinstance(payload, dict):
            return None

        request_data = payload.get("requestData") or payload.get("encryptedData") or payload.get("responseData")
        if request_data:
            return request_data

        nested_data = payload.get("data")
        if isinstance(nested_data, dict):
            return nested_data.get("requestData") or nested_data.get("encryptedData") or nested_data.get("responseData")

        return None

    @staticmethod
    def build_signzy_error_response(response, data, default_error_message):
        error_block = data.get("error") if isinstance(data, dict) else None
        if isinstance(error_block, dict):
            message = error_block.get("message") or default_error_message
            upstream_status = error_block.get("statusCode") or error_block.get("status") or response.status_code
            if 400 <= upstream_status < 500:
                http_status = upstream_status
            else:
                http_status = status.HTTP_502_BAD_GATEWAY

            return Response(
                {
                    "success": False,
                    "error": message,
                    "reason": error_block.get("reason"),
                    "status_code": response.status_code,
                    "data": data,
                },
                status=http_status,
            )

        if 400 <= response.status_code < 500:
            http_status = response.status_code
        else:
            http_status = status.HTTP_502_BAD_GATEWAY

        return Response(
            {
                "success": False,
                "error": default_error_message,
                "status_code": response.status_code,
                "data": data,
            },
            status=http_status,
        )

    @staticmethod
    def decrypt_signzy_payload(request_data):
        try:
            response = decrypt_data(request_data=request_data)
        except (Timeout, RequestException) as exc:
            return None, Response(
                {"success": False, "error": "Failed to reach Signzy decrypt_data API", "details": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        data = CrifBureauService.json_or_text(response)
        if 200 <= response.status_code < 300:
            return data, None

        return None, Response(
            {
                "success": False,
                "error": "Signzy decrypt_data API returned an error",
                "status_code": response.status_code,
                "data": data,
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    @staticmethod
    def enrich_payload_with_phone_data(payload, phone_to_pan_data):
        response_block = phone_to_pan_data.get("response") if isinstance(phone_to_pan_data, dict) else {}
        personal_info = response_block.get("personalInfo", {}) if isinstance(response_block, dict) else {}

        if not payload.get("panNumber"):
            payload["panNumber"] = response_block.get("pan")
        if not payload.get("gender"):
            payload["gender"] = personal_info.get("gender")
        if not payload.get("dateOfBirth"):
            payload["dateOfBirth"] = personal_info.get("dateOfBirth")

        missing_fields = [field for field in ("panNumber", "gender", "dateOfBirth") if not payload.get(field)]
        return payload, missing_fields

    @staticmethod
    def build_crif_payload(request_data):
        serializer = SendCrifRequestSerializer(data=request_data)
        if not serializer.is_valid():
            return None, Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        payload = serializer.validated_data.copy()

        try:
            phone_to_pan_response = phone_to_pan(
                mobile_number=payload["phoneNumber"],
                first_name=payload["firstName"],
                last_name=payload["lastName"],
            )
        except (Timeout, RequestException) as exc:
            return None, Response(
                {"success": False, "error": "Failed to reach Signzy phone_to_pan API", "details": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        phone_to_pan_data = CrifBureauService.json_or_text(phone_to_pan_response)
        if not (200 <= phone_to_pan_response.status_code < 300):
            return None, CrifBureauService.build_signzy_error_response(
                phone_to_pan_response,
                phone_to_pan_data,
                "Signzy phone_to_pan API returned an error",
            )

        payload, missing_fields = CrifBureauService.enrich_payload_with_phone_data(payload, phone_to_pan_data)
        if missing_fields:
            return None, Response(
                {
                    "success": False,
                    "error": "Missing required fields for CRIF request after phone_to_pan enrichment.",
                    "missing_fields": missing_fields,
                    "phone_to_pan_data": phone_to_pan_data,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return payload, None
