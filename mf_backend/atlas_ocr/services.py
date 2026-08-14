import requests
from django.conf import settings


class AtlasConfigurationError(Exception):
    pass


class AtlasAPIError(Exception):
    def __init__(self, message, status_code=502, details=None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details


class AtlasGoldPledgeCardClient:
    def __init__(self):
        self.base_url = settings.ATLAS_DOCSTREAM_BASE_URL.rstrip("/")
        self.client_id = settings.ATLAS_CLIENT_ID
        self.client_secret = settings.ATLAS_CLIENT_SECRET
        self.product_type = settings.ATLAS_PRODUCT_TYPE
        self.timeout = settings.ATLAS_REQUEST_TIMEOUT

        if not self.client_id or not self.client_secret:
            raise AtlasConfigurationError(
                "Atlas credentials are not configured on the server."
            )

    @staticmethod
    def _response_json(response):
        try:
            return response.json()
        except ValueError:
            return {"message": response.text or "Atlas returned an empty response."}

    def _raise_for_error(self, response, fallback_message):
        if response.ok:
            return

        details = self._response_json(response)
        # Do not pass provider 5xx status codes directly to clients.
        status_code = response.status_code if response.status_code < 500 else 502
        raise AtlasAPIError(
            details.get("message") or details.get("error") or fallback_message,
            status_code=status_code,
            details=details,
        )

    def _get_access_token(self):
        try:
            response = requests.post(
                f"{self.base_url}/v1/docstream/authtoken",
                headers={
                    "Client-Id": self.client_id,
                    "Client-Secret": self.client_secret,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise AtlasAPIError("Could not connect to Atlas authentication.") from exc

        self._raise_for_error(response, "Atlas authentication failed.")
        token = self._response_json(response).get("access_token")
        if not token:
            raise AtlasAPIError("Atlas authentication response did not contain a token.")
        return token

    def submit(self, file_urls, document_id=None):
        # Preserve compatibility for callers using submit(file_url, document_id).
        if isinstance(file_urls, str):
            file_urls = [{"file_url": file_urls, "document_id": document_id}]

        token = self._get_access_token()
        try:
            response = requests.post(
                f"{self.base_url}/v1/docstream/multiupload",
                headers={"Token": token, "Content-Type": "application/json"},
                json={
                    "product_type": self.product_type,
                    "file_urls": file_urls,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise AtlasAPIError("Could not connect to Atlas document upload.") from exc

        self._raise_for_error(response, "Atlas rejected the document upload.")
        data = self._response_json(response)
        if not data.get("batch_id"):
            raise AtlasAPIError("Atlas upload response did not contain a batch ID.")
        return data

    def get_result(self, batch_id, page=1, per_page=50):
        token = self._get_access_token()
        try:
            response = requests.get(
                f"{self.base_url}/v1/docstream/extracts",
                headers={"Token": token},
                params={
                    "batch_id": batch_id,
                    "page": page,
                    "per_page": per_page,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise AtlasAPIError("Could not connect to Atlas OCR results.") from exc

        self._raise_for_error(response, "Atlas could not retrieve OCR results.")
        return self._response_json(response)
