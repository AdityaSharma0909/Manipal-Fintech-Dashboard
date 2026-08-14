from types import SimpleNamespace

from django.test import SimpleTestCase

from onboarding_v2.constants import (
    ApplicationStatus,
    ApplicationStage,
    FundTransferredBy,
    LeadType,
    PaymentMode,
    TransactionStatus,
)
from onboarding_v2.helpers.fund_refund_helpers import update_bt_return_completed_status
from onboarding_v2.serializers import FundRefundSerializer


class _StageSnapshots:
    def get(self, stage):
        if stage != ApplicationStage.LOAN:
            raise AssertionError(f"Unexpected stage lookup: {stage}")
        return SimpleNamespace(payload={"requested_amount": "100.00"})


class FundRefundValidationTests(SimpleTestCase):
    def setUp(self):
        self.application = SimpleNamespace(
            lead=SimpleNamespace(amount="0.00"),
            loan_type=LeadType.BALANCE_TRANSFER,
            stage_snapshots=_StageSnapshots(),
            stage_payload={
                "fund_refund": [
                    {
                        "amount": "60.00",
                        "status": TransactionStatus.VERIFIED,
                    }
                ]
            },
        )

    def _payload(self, amount):
        return {
            "amount": amount,
            "payment_mode": PaymentMode.NEFT,
            "bank_name": "Karnataka Bank",
            "transaction_reference_number": "1234567",
            "fund_transferred_by": FundTransferredBy.SELF,
            "cheque_image_url": "https://example.com/cheque.jpg",
            "transaction_proof_url": "https://example.com/proof.jpg",
        }

    def test_uses_bt_loan_snapshot_amount_for_pending_amount(self):
        serializer = FundRefundSerializer(
            data=self._payload("40.00"),
            context={"application": self.application, "is_complete": True},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_accepts_two_cheque_image_urls(self):
        payload = self._payload("40.00")
        payload.pop("cheque_image_url")
        payload["cheque_image_urls"] = [
            "https://example.com/cheque-front.jpg",
            "https://example.com/cheque-back.jpg",
        ]

        serializer = FundRefundSerializer(
            data=payload,
            context={"application": self.application, "is_complete": True},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["cheque_image_url"], "https://example.com/cheque-front.jpg")
        self.assertEqual(serializer.validated_data["cheque_image_urls"], payload["cheque_image_urls"])

    def test_rejects_amount_above_snapshot_pending_amount(self):
        serializer = FundRefundSerializer(
            data=self._payload("41.00"),
            context={"application": self.application, "is_complete": True},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("amount", serializer.errors)

    def test_rejects_duplicate_transaction_reference_number(self):
        self.application.stage_payload["fund_refund"][0]["transaction_reference_number"] = "1234567"
        
        serializer = FundRefundSerializer(
            data=self._payload("40.00"),
            context={"application": self.application, "is_complete": True},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("transaction_reference_number", serializer.errors)
        self.assertEqual(serializer.errors["transaction_reference_number"][0], "This transaction reference number has already been used for this application.")

    def test_accepts_refund_when_legacy_stage_payload_is_a_list(self):
        self.application.stage_payload = []

        serializer = FundRefundSerializer(
            data=self._payload("40.00"),
            context={"application": self.application, "is_complete": True},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_updates_status_when_refund_submission_covers_sanctioned_amount(self):
        class Application(SimpleNamespace):
            def save(self, update_fields=None):
                self.saved_update_fields = update_fields

        application = Application(
            lead=SimpleNamespace(amount="0.00"),
            loan_type=LeadType.BALANCE_TRANSFER,
            status=ApplicationStatus.AMOUNT_NOT_PAID_TO_EXISTING_LENDER,
            stage_snapshots=_StageSnapshots(),
            stage_payload={
                "fund_refund": [
                    {
                        "amount": "100.00",
                        "status": TransactionStatus.VERIFIED,
                    }
                ]
            },
        )

        updated = update_bt_return_completed_status(
            application,
            ApplicationStatus.AMOUNT_NOT_PAID_TO_EXISTING_LENDER,
        )

        self.assertTrue(updated)
        self.assertEqual(
            application.status,
            ApplicationStatus.AMOUNT_NOT_PAID_TO_EXISTING_LENDER_BT_RETURN_COMPLETED,
        )
        self.assertEqual(application.saved_update_fields, ["status", "modified_at"])

    def test_does_not_update_status_when_previous_status_is_not_a_return_branch(self):
        class Application(SimpleNamespace):
            def save(self, update_fields=None):
                raise AssertionError("Save should not be called")

        application = Application(
            lead=SimpleNamespace(amount="0.00"),
            loan_type=LeadType.BALANCE_TRANSFER,
            status=ApplicationStatus.AMOUNT_PAID_TO_EXISTING_LENDER,
            stage_snapshots=_StageSnapshots(),
            stage_payload={
                "fund_refund": [
                    {
                        "amount": "100.00",
                        "status": TransactionStatus.VERIFIED,
                    }
                ]
            },
        )

        updated = update_bt_return_completed_status(
            application,
            ApplicationStatus.AMOUNT_PAID_TO_EXISTING_LENDER,
        )

        self.assertFalse(updated)
        self.assertEqual(application.status, ApplicationStatus.AMOUNT_PAID_TO_EXISTING_LENDER)
