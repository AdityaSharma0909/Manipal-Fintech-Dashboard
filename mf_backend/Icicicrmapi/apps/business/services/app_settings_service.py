from typing import Optional
from apps.business.services.base_service import BaseService
from apps.data.repositories.app_settings_repository import AppSettingsRepository
from apps.models.icici_app_settings_model import IciciAppSetting


class AppSettingsService(BaseService):
    """
    Business service for managing ICICI Application Settings.
    """
    def __init__(self, repository: AppSettingsRepository):
        super().__init__()
        self._repository = repository

    def get_settings_by_bank_id(self, bank_id: int) -> Optional[IciciAppSetting]:
        """
        Retrieves ICICI settings for a specific bank.
        """
        return self._repository.get_by_bank_id(bank_id)

    def get_default_settings(self) -> Optional[IciciAppSetting]:
        """
        Retrieves default ICICI settings (Bank ID 1).
        """
        return self.get_settings_by_bank_id(1)
