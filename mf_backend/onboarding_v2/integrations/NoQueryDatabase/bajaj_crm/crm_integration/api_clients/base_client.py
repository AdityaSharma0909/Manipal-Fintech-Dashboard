import os
import time
import httpx
import logging
from datetime import datetime
from django.conf import settings
from crm_integration.middleware import get_correlation_id

logger = logging.getLogger(__name__)


class BaseHttpClient:
    """Base client implementing timeout handling, request logging, and correlation ID forwarding."""
    
    def __init__(self):
        self.timeout = httpx.Timeout(15.0, connect=5.0)
        # Using a connection pool with limit settings
        self.limits = httpx.Limits(max_keepalive_connections=5, max_connections=20)

    def _log_to_file(self, message: str, file_prefix: str, directory_name: str):
        """Appends API log details to daily text files to match the C# implementation."""
        try:
            base_dir = settings.FILE_STORAGE.get('BASE_PATH')
            if not base_dir:
                return

            now = datetime.now()
            # Path structure: BASE_PATH/YYYY/MM/DD/directory_name/file_prefix.txt
            folder_path = os.path.join(
                base_dir,
                str(now.year),
                f"{now.month:02d}",
                f"{now.day:02d}",
                directory_name
            )
            os.makedirs(folder_path, exist_ok=True)
            
            file_path = os.path.join(folder_path, f"{file_prefix}.txt")
            log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            log_message = f"{log_time} - {message}\n\n"

            # Sync file write with append mode
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(log_message)
        except Exception as ex:
            logger.error(f"Error writing request/response log file: {str(ex)}")

    async def _send_request(
        self,
        method: str,
        url: str,
        headers: dict = None,
        data: dict = None,
        json_data: dict = None,
        file_prefix: str = None,
        directory_name: str = None
    ) -> httpx.Response:
        headers = headers or {}
        
        # Attach Correlation ID
        corr_id = get_correlation_id()
        if corr_id:
            headers['X-Correlation-ID'] = corr_id
            
        request_body = str(json_data or data or "")
        
        # Log Request (Standard Logger & File Logger)
        logger.info(f"Outgoing Request: {method} {url} | Headers: {headers}")
        if file_prefix and directory_name:
            self._log_to_file(
                f"Request URL: {url}\nRequest Headers: {headers}\nRequest Body: {request_body}",
                file_prefix,
                directory_name
            )

        start_time = time.monotonic()
        async with httpx.AsyncClient(limits=self.limits, timeout=self.timeout) as client:
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    data=data,
                    json=json_data
                )
                print(response.status_code)
                # print("i am vicky")
                print(response.text)
                elapsed = time.monotonic() - start_time
                # Log Response
                masked_headers = {k: (v if k.lower() not in ('authorization', 'ocp-apim-subscription-key') else v[:6] + '****') for k, v in dict(response.headers).items()}
                logger.info(
                    f"Response Status: {response.status_code} | "
                    f"Execution Time: {elapsed:.3f}s | "
                    f"URL: {url}"
                )
                logger.info(f"Response Headers: {masked_headers}")
                logger.info(f"Response Body: {response.text[:2000]}")
                if file_prefix and directory_name:
                    self._log_to_file(
                        f"Response Status: {response.status_code}\n"
                        f"Response Headers: {dict(response.headers)}\n"
                        f"Response Body: {response.text}\n"
                        f"Execution Time: {elapsed:.3f}s",
                        file_prefix,
                        directory_name
                    )
                return response
            except httpx.HTTPError as ex:
                elapsed = time.monotonic() - start_time
                logger.error(f"HTTP Request failed: {str(ex)} | Execution Time: {elapsed:.3f}s")
                if file_prefix and directory_name:
                    self._log_to_file(
                        f"EXCEPTION: {str(ex)}\nExecution Time: {elapsed:.3f}s",
                        file_prefix,
                        directory_name
                    )
                raise
