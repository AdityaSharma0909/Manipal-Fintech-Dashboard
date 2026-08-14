import pytest
from crm_integration.serializers import CreateBajajFinServoLeadInitialRequestSerializer
from crm_integration.services.lead_type_configuration import LeadTypeConfigurationProvider


def test_lead_type_configuration_provider_returns_expected_values():
    configs = {
        'balance transfer': {
            'HEADER_SOURCE': 'MFPL BT',
            'LEAD_SOURCE': 'MFPL BT',
            'LEAD_ORIGIN': 'MFPL BT',
            'LEAD_CHANNEL': 'MFPL BT',
            'SRC': 'MFPL BT',
            'PRODUCT': 'MFPL BT',
            'REFERRAL_PARTNER': 'MFPL BT',
        },
        'fresh lead': {
            'HEADER_SOURCE': 'MFPL FL',
            'LEAD_SOURCE': 'MFPL FL',
            'LEAD_ORIGIN': 'MFPL FL',
            'LEAD_CHANNEL': 'MFPL FL',
            'SRC': 'MFPL FL',
            'PRODUCT': 'MFPL FL',
            'REFERRAL_PARTNER': 'MFPL FL',
        }
    }

    provider = LeadTypeConfigurationProvider(configs=configs)
    config = provider.get_configuration('Balance Transfer')

    assert config.header_source == 'MFPL BT'
    assert config.lead_source == 'MFPL BT'
    assert config.lead_origin == 'MFPL BT'
    assert config.lead_channel == 'MFPL BT'
    assert config.src == 'MFPL BT'
    assert config.product == 'MFPL BT'
    assert config.referral_partner == 'MFPL BT'

    config = provider.get_configuration('fresh lead')
    assert config.header_source == 'MFPL FL'
    assert config.lead_source == 'MFPL FL'
    assert config.referral_partner == 'MFPL FL'


def test_lead_type_configuration_provider_rejects_unsupported_type():
    provider = LeadTypeConfigurationProvider(configs={'balance transfer': {}})

    with pytest.raises(ValueError, match="Unsupported Type"):
        provider.get_configuration('personal loan')


def test_create_lead_serializer_rejects_unknown_type():
    payload = {
        'FullName': 'Vicky Yadav',
        'MobileNo': '9372364859',
        'LoanAmount': 20400,
        'Branch': '32292',
        'Type': 'unknown type'
    }
    serializer = CreateBajajFinServoLeadInitialRequestSerializer(data=payload)

    assert not serializer.is_valid()
    assert 'Type' in serializer.errors
