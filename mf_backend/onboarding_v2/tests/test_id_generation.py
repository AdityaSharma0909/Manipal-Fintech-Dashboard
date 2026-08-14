from django.test import TestCase

from onboarding_v2.services import (
    generate_application_id,
    generate_customer_id,
    generate_lead_code,
)


class IdGenerationTests(TestCase):
    def test_customer_id_sequence_rolls_prefix(self):
        ids = [generate_customer_id() for _ in range(10002)]
        self.assertEqual(ids[0], "AAA0001")
        self.assertEqual(ids[1], "AAA0002")
        # 10000th -> AAA0001 + 9999 -> AAA10000? but limited to 4 digits so rollover
        self.assertEqual(ids[9999], "AAA10000")  # 10,000th under same prefix
        # 10001st should roll prefix to AAB0001
        self.assertEqual(ids[10000], "AAB0001")

    def test_lead_and_app_sequences_per_prefix(self):
        lead1 = generate_lead_code("Gold Loan")
        lead2 = generate_lead_code("Gold Loan")
        lead_other = generate_lead_code("Home Loan")
        self.assertEqual(lead1, "GL0001")
        self.assertEqual(lead2, "GL0002")
        self.assertEqual(lead_other, "HL0001")

        app1 = generate_application_id("Gold Loan")
        app2 = generate_application_id("Gold Loan")
        app_other = generate_application_id("Home Loan")
        self.assertEqual(app1, "MPAGL0001")
        self.assertEqual(app2, "MPAGL0002")
        self.assertEqual(app_other, "MPAHL0001")
