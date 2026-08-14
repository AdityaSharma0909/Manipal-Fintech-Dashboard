from typing import Optional
from apps.data.repositories.base_repository import BaseRepository
from apps.models.icici_request_log_model import IciciRequestLog
from apps.models.icici_bank_response_log_model import IciciBankResponseLog


class RequestLogRepository(BaseRepository[IciciRequestLog]):
    """
    Repository for ICICI Request Logs.
    """
    model = IciciRequestLog

    def get_by_correlation_id(self, correlation_id: str) -> Optional[IciciRequestLog]:
        return self.get_queryset().filter(correlation_id=correlation_id).first()


class ResponseLogRepository(BaseRepository[IciciBankResponseLog]):
    """
    Repository for ICICI Bank Response Logs.
    """
    model = IciciBankResponseLog

    def get_by_request_id(self, request_id: str) -> Optional[IciciBankResponseLog]:
        return self.get_queryset().filter(request_log_id=request_id).first()
