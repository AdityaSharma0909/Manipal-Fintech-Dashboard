from django.test import SimpleTestCase

from onboarding_v2.admin import ProductV2Admin


class ProductV2AdminDropdownTests(SimpleTestCase):
    def setUp(self):
        self.form = ProductV2Admin.ProductV2AdminForm()

    def test_available_for_is_multi_select(self):
        self.assertEqual(
            list(self.form.fields["available_for"].choices),
            [
                ("CO_LENDING", "Co-Lending"),
                ("SELF_LENDING", "Self-Lending"),
            ],
        )
        self.assertEqual(
            self.form.fields["available_for"].widget.__class__.__name__,
            "SelectMultiple",
        )

    def test_workbook_values_are_dropdown_choices(self):
        self.assertEqual(
            list(self.form.fields["category"].choices),
            [
                ("", "---------"),
                ("CONSUMPTION_LOAN", "Consumption Loan"),
                ("INCOME_LOAN", "Income Loan"),
            ],
        )
        self.assertEqual(
            list(self.form.fields["repayment_frequency"].choices),
            [
                ("", "---------"),
                ("BULLET", "Bullet"),
                ("QUARTERLY", "Quarterly"),
                ("MONTHLY", "Monthly"),
            ],
        )
        self.assertEqual(
            list(self.form.fields["tenure_months"].choices),
            [
                ("", "---------"),
                (3, "3 months"),
                (4, "4 months"),
                (6, "6 months"),
                (9, "9 months"),
                (12, "12 months"),
            ],
        )
