from django.test import SimpleTestCase

from onboarding_v2.serializers import GoldPacketSerializer


class GoldPacketValidationTests(SimpleTestCase):
    def test_packet_totals_match_items(self):
        payload = {
            "packet_id": "PKT-1",
            "gross_weight": "30",
            "gross_value": "3000",
            "net_adjusted_weight": "27",
            "net_adjusted_value": "2700",
            "items": [
                {
                    "type_of_jewellery": "ANKLET",
                    "number_of_articles": 1,
                    "gross_weight": "10",
                    "net_weight": "9",
                    "gross_value": "1000",
                    "net_adjusted_weight": "9",
                    "net_adjusted_value": "900",
                },
                {
                    "type_of_jewellery": "ANKLET",
                    "number_of_articles": 1,
                    "gross_weight": "20",
                    "net_weight": "18",
                    "gross_value": "2000",
                    "net_adjusted_weight": "18",
                    "net_adjusted_value": "1800",
                },
            ],
        }
        serializer = GoldPacketSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_packet_totals_mismatch_returns_errors(self):
        payload = {
            "packet_id": "PKT-2",
            "gross_weight": "10",
            "gross_value": "1000",
            "net_adjusted_weight": "9",
            "net_adjusted_value": "900",
            "items": [
                {
                    "type_of_jewellery": "ANKLET",
                    "number_of_articles": 1,
                    "gross_weight": "10",
                    "net_weight": "9",
                    "gross_value": "1000",
                    "net_adjusted_weight": "9",
                    "net_adjusted_value": "900",
                },
                {
                    "type_of_jewellery": "ANKLET",
                    "number_of_articles": 1,
                    "gross_weight": "1",
                    "net_weight": "1",
                    "gross_value": "100",
                    "net_adjusted_weight": "1",
                    "net_adjusted_value": "100",
                },
            ],
        }
        serializer = GoldPacketSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("gross_weight", serializer.errors)
        self.assertIn("gross_value", serializer.errors)
        self.assertIn("net_adjusted_weight", serializer.errors)
        self.assertIn("net_adjusted_value", serializer.errors)
