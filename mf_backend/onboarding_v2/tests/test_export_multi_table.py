import io

import pandas as pd
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from onboarding_v2.constants import LeadType
from onboarding_v2.models import ApplicationV2, LeadV2, LoanPunchV2
from onboarding_v2.views.export_multi_table import build_multi_table_export_workbook


User = get_user_model()


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
)
class MultiTableExportWorkbookTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="gl-report-agent",
            password="pass",
            phone="9000000001",
            role="LOAN_OFFICER",
            employee_id="EMP002",
        )
        self.lead = LeadV2.objects.create(
            customer_id="CUST-MULTI-LOAN",
            contact_number="9876543211",
            customer_name="Multiple Loan Customer",
            product_category="LOAN",
            assigned_to=self.user,
        )
        self.application = ApplicationV2.objects.create(
            application_id="APP-MULTI-LOAN",
            lead=self.lead,
            loan_type=LeadType.FRESH,
            lending_partner="Test Bank",
        )

    def test_includes_every_loan_for_an_application(self):
        LoanPunchV2.objects.create(
            application=self.application,
            bank_name="Test Bank",
            crm_id="CRM-ONE",
            loan_account_number="LOAN-ACCOUNT-ONE",
            sanctioned_amount=100000,
        )
        LoanPunchV2.objects.create(
            application=self.application,
            bank_name="Test Bank",
            crm_id="CRM-TWO",
            loan_account_number="LOAN-ACCOUNT-TWO",
            sanctioned_amount=200000,
        )

        workbook, row_count = build_multi_table_export_workbook(
            ApplicationV2.objects.filter(pk=self.application.pk)
        )
        report = pd.read_excel(io.BytesIO(workbook.getvalue()), engine="openpyxl")

        self.assertEqual(row_count, 2)
        self.assertEqual(len(report), 2)
        self.assertEqual(
            set(report["Loan Account Number (Punching)"]),
            {"LOAN-ACCOUNT-ONE", "LOAN-ACCOUNT-TWO"},
        )
        self.assertEqual(set(report["Application ID"]), {"APP-MULTI-LOAN"})

    def test_keeps_application_without_a_punched_loan(self):
        workbook, row_count = build_multi_table_export_workbook(
            ApplicationV2.objects.filter(pk=self.application.pk)
        )
        report = pd.read_excel(io.BytesIO(workbook.getvalue()), engine="openpyxl")

        self.assertEqual(row_count, 1)
        self.assertEqual(len(report), 1)
        self.assertEqual(report.iloc[0]["Application ID"], "APP-MULTI-LOAN")
