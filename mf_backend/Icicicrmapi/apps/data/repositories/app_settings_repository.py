from typing import Optional
from apps.data.repositories.base_repository import BaseRepository
from apps.models.icici_app_settings_model import IciciAppSetting


class AppSettingsRepository(BaseRepository[IciciAppSetting]):
    """
    Repository for managing ICICI Application Settings.
    """
    model = IciciAppSetting

    def get_by_bank_id(self, bank_id: int) -> Optional[IciciAppSetting]:
        """
        Fetch settings for a specific bank ID.
        """
        return self.get_queryset().filter(bank_id=bank_id).first()
