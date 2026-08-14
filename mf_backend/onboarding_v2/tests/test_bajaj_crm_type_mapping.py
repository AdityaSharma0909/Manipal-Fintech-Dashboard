from unittest.mock import patch

from django.test import SimpleTestCase

from onboarding_v2.constants import LeadType
from onboarding_v2.integrations.bajaj.mapping import build_bajaj_create_lead_data
from onboarding_v2.integrations.bajaj.settings import BajajCrmTypeConfig, BajajEnvConfig
from onboarding_v2.models import LeadV2
from onboarding_v2.serializers import LeadCreateSerializer


def _config() -> BajajEnvConfig:
    return BajajEnvConfig(
        base_api_url="https://example.com",
        save_lead_endpoint="/save",
        ocp_apim_subscription_key="subscription-key",
        header_source="BASE_HEADER",
        shared_secret_key="key",
        shared_secret_iv="iv",
        microsoft_token_url="https://login.example.com/token",
        microsoft_client_id="client-id",
        microsoft_client_secret="client-secret",
        microsoft_resource="resource",
        microsoft_scope="scope",
        lead_source="BASE_SOURCE",
        lead_origin="BASE_ORIGIN",
        lead_channel="BASE_CHANNEL",
        src="BASE_SRC",
        product="BASE_PRODUCT",
        referral_partner="BASE_PARTNER",
        crm_type_configs={
            "BALANCE_TRANSFER": BajajCrmTypeConfig(
                header_source="BT_HEADER",
                lead_source="BT_SOURCE",
                lead_origin="BT_ORIGIN",
                lead_channel="BT_CHANNEL",
                src="BT_SRC",
                product="BT_PRODUCT",
                referral_partner="BT_PARTNER",
            ),
            "FRESH": BajajCrmTypeConfig(
                header_source="FRESH_HEADER",
                lead_source="FRESH_SOURCE",
                lead_origin="FRESH_ORIGIN",
                lead_channel="FRESH_CHANNEL",
                src="FRESH_SRC",
                product="FRESH_PRODUCT",
                referral_partner="FRESH_PARTNER",
            ),
        },
    )


class BajajCrmTypeMappingTests(SimpleTestCase):
    @patch("onboarding_v2.serializers.LeadV2.objects.filter")
    def test_lead_serializer_moves_crm_type_to_metadata(self, mock_filter) -> None:
        class EmptyLeadQuerySet:
            def exclude(self, *args, **kwargs):
                return self

            def prefetch_related(self, *args, **kwargs):
                return []

        mock_filter.return_value = EmptyLeadQuerySet()
        serializer = LeadCreateSerializer(data={
            "contact_number": "9651815264",
            "customer_name": "Karan txvv",
            "product_category": "LOAN",
            "product_subcategory": "GOLD_LOAN",
            "amount": "807800",
            "source": "SELF",
            "lead_type": LeadType.BANK_LEAD,
            "pincode": "560102",
            "bank": "Bajaj Finserv",
            "crm_type": "BALANCE_TRANSFER",
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("crm_type", serializer.validated_data)
        self.assertEqual(serializer.validated_data["metadata"]["crm_type"], "BALANCE_TRANSFER")

    def test_balance_transfer_crm_type_selects_bt_bajaj_values(self) -> None:
        lead = LeadV2(
            contact_number="9651815264",
            customer_name="Karan txvv",
            amount="807800",
            pincode="560102",
            lead_type=LeadType.BANK_LEAD,
            metadata={"crm_type": "BALANCE_TRANSFER"},
        )

        result = build_bajaj_create_lead_data(lead=lead, config=_config())

        self.assertEqual(result.header_source, "BT_HEADER")
        self.assertEqual(result.bajaj_data["product"], "BT_PRODUCT")
        self.assertEqual(result.bajaj_data["lead_source"], "BT_SOURCE")
        self.assertEqual(result.bajaj_data["lead_origin"], "BT_ORIGIN")
        self.assertEqual(result.bajaj_data["lead_channel"], "BT_CHANNEL")
        self.assertEqual(result.bajaj_data["src"], "BT_SRC")
        self.assertEqual(result.bajaj_data["referral_partner"], "BT_PARTNER")

    def test_fresh_crm_type_selects_fresh_bajaj_values(self) -> None:
        lead = LeadV2(
            contact_number="9651815265",
            customer_name="Fresh Customer",
            amount="807800",
            pincode="560102",
            lead_type=LeadType.BANK_LEAD,
            metadata={"crm_type": "FRESH"},
        )

        result = build_bajaj_create_lead_data(lead=lead, config=_config())

        self.assertEqual(result.header_source, "FRESH_HEADER")
        self.assertEqual(result.bajaj_data["product"], "FRESH_PRODUCT")
        self.assertEqual(result.bajaj_data["lead_source"], "FRESH_SOURCE")

    def test_missing_crm_type_keeps_default_bajaj_values(self) -> None:
        lead = LeadV2(
            contact_number="9651815266",
            customer_name="Default Customer",
            amount="807800",
            pincode="560102",
            lead_type=LeadType.BANK_LEAD,
            metadata={},
        )

        result = build_bajaj_create_lead_data(lead=lead, config=_config())

        self.assertEqual(result.header_source, "BASE_HEADER")
        self.assertEqual(result.bajaj_data["product"], "BASE_PRODUCT")
        self.assertEqual(result.bajaj_data["lead_source"], "BASE_SOURCE")
