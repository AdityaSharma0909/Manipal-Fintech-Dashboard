from django.test import SimpleTestCase

from onboarding_v2.helpers.persistence_helpers import normalize_bt_waiver_payload


class NormalizeBTWaiverPayloadTests(SimpleTestCase):
    def test_opted_out_payload_removes_stale_waiver_fields(self):
        payload = {
            "waiver_opted": False,
            "waiver_percentage": "10",
            "remarks": "Customer requested partial waiver",
            "proof_1_url": "https://example.com/proof.jpg",
            "proof_2_url": None,
        }

        self.assertEqual(
            normalize_bt_waiver_payload(payload),
            {"waiver_opted": False},
        )

    def test_opted_in_payload_is_unchanged(self):
        payload = {
            "waiver_opted": True,
            "waiver_percentage": "10",
            "proof_1_url": "https://example.com/proof.jpg",
        }

        self.assertIs(normalize_bt_waiver_payload(payload), payload)
