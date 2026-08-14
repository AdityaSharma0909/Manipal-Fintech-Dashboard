from dataclasses import dataclass
from django.conf import settings


@dataclass(frozen=True)
class LeadTypeConfiguration:
    header_source: str
    lead_source: str
    lead_origin: str
    lead_channel: str
    src: str
    product: str
    referral_partner: str


class LeadTypeConfigurationProvider:
    """Provides complete Bajaj lead request configuration by incoming Type."""

    def __init__(self, configs: dict | None = None):
        self.configs = configs if configs is not None else getattr(settings, 'BAJAJ_LEAD_TYPE_CONFIGS', {})

    def get_configuration(self, type_name: str) -> LeadTypeConfiguration:
        if not isinstance(type_name, str) or not type_name.strip():
            raise ValueError('Type must be a non-empty string.')

        normalized_type = type_name.strip().lower()
        type_config = self.configs.get(normalized_type)

        if type_config is None:
            supported = ", ".join(sorted(self.configs.keys()))
            raise ValueError(
                f"Unsupported Type '{type_name}'. Supported types: {supported}"
            )

        return LeadTypeConfiguration(
            header_source=type_config['HEADER_SOURCE'],
            lead_source=type_config['LEAD_SOURCE'],
            lead_origin=type_config['LEAD_ORIGIN'],
            lead_channel=type_config['LEAD_CHANNEL'],
            src=type_config['SRC'],
            product=type_config['PRODUCT'],
            referral_partner=type_config['REFERRAL_PARTNER'],
        )
