import json
from django.test import Client, TestCase, override_settings

from onboarding_v2.constants import ApplicationStage
from onboarding_v2.models import ApplicationStageSnapshot, ApplicationV2, BankDetailsV2, LeadV2
from users.models import User


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class StageSnapshotMergeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="merge_user",
            phone="+911234567890",
            role="ADMIN",
            first_name="Merge",
            last_name="User",
        )
        self.lead = LeadV2.objects.create(
            customer_id="CUST-100",
            contact_number="9999999999",
            customer_name="Merge User",
            product_category="LOAN",
            created_by=self.user,
            assigned_to=self.user,
        )
        self.app = ApplicationV2.objects.create(application_id="APP-MERGE-1", lead=self.lead)

    def _post_stage(self, stage, payload, is_complete=False):
        return self.client.post(
            f"/api/v2/onboarding/applications/{self.app.application_id}/stage/",
            data=json.dumps({"stage": stage, "payload": payload, "is_complete": is_complete}),
            content_type="application/json",
        )

    def test_basic_stage_merge_keeps_optional_fields(self):
        base_payload = {
            "full_name_as_pan": "Merge User",
            "dob": "1990-01-01",
            "dob_as_per_pan": "1990-01-01",
            "phone_number": "9999999999",
            "gender": "MALE",
            "aadhar_number": "123412341234",
            "email": "first@example.com",
            "alternate_number": "8888888888",
        }
        resp = self._post_stage(ApplicationStage.BASIC, base_payload)
        self.assertEqual(resp.status_code, 200)

        update_payload = {
            "full_name_as_pan": "Merge User",
            "dob": "1990-01-01",
            "dob_as_per_pan": "1990-01-01",
            "phone_number": "9999999999",
            "gender": "MALE",
            "aadhar_number": "123412341234",
        }
        resp = self._post_stage(ApplicationStage.BASIC, update_payload)
        self.assertEqual(resp.status_code, 200)

        snap = ApplicationStageSnapshot.objects.get(application=self.app, stage=ApplicationStage.BASIC)
        self.assertEqual(snap.payload.get("email"), "first@example.com")
        self.assertEqual(snap.payload.get("alternate_number"), "8888888888")

    def test_address_stage_merge_preserves_mailing(self):
        first_payload = {
            "permanent": {
                "address_line1": "Line 1",
                "pincode": "560001",
                "state": "KARNATAKA",
                "district": "BENGALURU URBAN",
                "city": "BENGALURU",
            },
            "current_same_as_permanent": True,
            "mailing": {
                "address_line1": "Mailing 1",
                "pincode": "560002",
                "state": "KARNATAKA",
                "district": "BENGALURU URBAN",
                "city": "BENGALURU",
            },
        }
        resp = self._post_stage(ApplicationStage.ADDRESS, first_payload)
        self.assertEqual(resp.status_code, 200)

        update_payload = {
            "permanent": {
                "address_line1": "Line 1 Updated",
                "pincode": "560001",
                "state": "KARNATAKA",
                "district": "BENGALURU URBAN",
                "city": "BENGALURU",
            },
            "current_same_as_permanent": True,
        }
        resp = self._post_stage(ApplicationStage.ADDRESS, update_payload)
        self.assertEqual(resp.status_code, 200)

        snap = ApplicationStageSnapshot.objects.get(application=self.app, stage=ApplicationStage.ADDRESS)
        self.assertEqual(snap.payload.get("permanent", {}).get("address_line1"), "Line 1 Updated")
        self.assertEqual(snap.payload.get("mailing", {}).get("address_line1"), "Mailing 1")

    def test_address_stage_accepts_poa_type(self):
        payload = {
            "permanent": {
                "address_line1": "Line 1",
                "pincode": "560001",
                "state": "KARNATAKA",
                "district": "BENGALURU URBAN",
                "city": "BENGALURU",
            },
            "current_same_as_permanent": True,
            "poa_type": "Gazetted office letter",
        }

        resp = self._post_stage(ApplicationStage.ADDRESS, payload)
        self.assertEqual(resp.status_code, 200)

        snap = ApplicationStageSnapshot.objects.get(application=self.app, stage=ApplicationStage.ADDRESS)
        self.assertEqual(snap.payload.get("poa_type"), "Gazetted office letter")

    def test_gold_stage_merge_by_item_index(self):
        first_payload = {
            "packet_id": "PKT-1",
            "barcode_id": "BAR-1",
            "items": [
                {
                    "type_of_jewellery": "RING",
                    "number_of_articles": 1,
                    "purity": "22",
                    "gross_weight": "10.000",
                    "net_weight": "9.500",
                    "net_adjusted_weight": "9.300",
                    "gross_value": "60000.00",
                    "net_adjusted_value": "58000.00",
                },
                {
                    "type_of_jewellery": "RING",
                    "number_of_articles": 1,
                    "purity": "22",
                    "gross_weight": "8.000",
                    "net_weight": "7.600",
                    "net_adjusted_weight": "7.400",
                    "gross_value": "50000.00",
                    "net_adjusted_value": "48000.00",
                },
            ],
        }
        resp = self._post_stage(ApplicationStage.GOLD, first_payload, is_complete=True)
        self.assertEqual(resp.status_code, 200)

        update_payload = {
            "packet_id": "PKT-1",
            "barcode_id": "BAR-1",
            "items": [
                {
                    "type_of_jewellery": "RING",
                    "item_index": 2,
                    "number_of_articles": 1,
                    "purity": "22",
                    "gross_weight": "8.000",
                    "net_weight": "7.600",
                    "net_adjusted_weight": "7.400",
                    "gross_value": "50000.00",
                    "net_adjusted_value": "48000.00",
                    "front_image_url": "https://cdn.example.com/ring2_front.jpg",
                }
            ],
        }
        resp = self._post_stage(ApplicationStage.GOLD, update_payload, is_complete=True)
        self.assertEqual(resp.status_code, 200)

        snap = ApplicationStageSnapshot.objects.get(application=self.app, stage=ApplicationStage.GOLD)
        items = snap.payload.get("items") or []
        self.assertEqual(len(items), 2)
        self.assertTrue(any(i.get("front_image_url") == "https://cdn.example.com/ring2_front.jpg" for i in items))

    def test_bank_stage_merge_metadata_cheque_url(self):
        first_payload = {
            "bank_name": "Axis Bank",
            "account_number": "1234567890",
            "customer_name_as_per_bank": "Merge User",
            "ifsc_code": "UTIB0000123",
            "branch_name": "Main",
        }
        resp = self._post_stage(ApplicationStage.BANK, first_payload, is_complete=True)
        self.assertEqual(resp.status_code, 200)

        update_payload = {
            "bank_name": "Axis Bank",
            "account_number": "1234567890",
            "customer_name_as_per_bank": "Merge User",
            "ifsc_code": "UTIB0000123",
            "branch_name": "Main",
            "metadata": {"cheque_image_url": "https://cdn.example.com/cheque.jpg"},
        }
        resp = self._post_stage(ApplicationStage.BANK, update_payload, is_complete=True)
        self.assertEqual(resp.status_code, 200)

        bank = BankDetailsV2.objects.get(application=self.app)
        self.assertEqual(bank.cheque_image_url, "https://cdn.example.com/cheque.jpg")
