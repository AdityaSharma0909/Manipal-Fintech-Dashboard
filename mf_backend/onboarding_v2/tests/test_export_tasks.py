import io
import pandas as pd
from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth import get_user_model

from onboarding_v2.constants import LeadType
from onboarding_v2.models import (
    ApplicationV2,
    LeadV2,
    LoanPunchV2,
)
from onboarding_v2.tasks import (
    export_bt_disbursal_report_task,
    export_new_gl_against_bt_report_task,
    export_tele_centre_report_task,
)

User = get_user_model()


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class ExportTasksTests(TestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username="agent",
            password="pass",
            phone="9000000000",
            role="LOAN_OFFICER",
            employee_id="EMP001",
        )

        # Create Balance Transfer Lead & Application
        self.lead = LeadV2.objects.create(
            customer_id="CUST-BT",
            contact_number="9876543210",
            customer_name="John Doe",
            product_category="LOAN",
            assigned_to=self.user,
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-BT",
            lead=self.lead,
            loan_type=LeadType.BALANCE_TRANSFER,
            van_number="VAN-TEST-12345",
        )

        # Create a LoanPunchV2 to verify New GL Against BT fields
        self.loan_punch = LoanPunchV2.objects.create(
            application=self.app,
            bank_name="Exiting Bank Test",
            new_bank_name="New Bank Test",
            sanctioned_amount=500000,
            loan_account_number="ACC123456",
        )

    def test_export_bt_disbursal_report_task(self):
        mail.outbox.clear()
        result = export_bt_disbursal_report_task(recipient_email="test-bt@example.com")
        self.assertIn("BT Disbursal Report containing 1 records sent to test-bt@example.com", result)
        self.assertEqual(len(mail.outbox), 1)

        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, "BT Disbursal Report")
        self.assertIn("Total BT Disbursal Records", sent_email.alternatives[0][0])
        self.assertEqual(len(sent_email.attachments), 1)

        attachment_name, attachment_content, content_type = sent_email.attachments[0]
        self.assertTrue(attachment_name.startswith("bt_disbursal_report_"))
        self.assertTrue(attachment_name.endswith(".xlsx"))

        # Verify Excel content
        excel_data = io.BytesIO(attachment_content)
        df = pd.read_excel(excel_data, engine="openpyxl")
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["FLID"], "APP-BT")
        self.assertEqual(df.iloc[0]["VAN Number"], "VAN-TEST-12345")

    def test_export_new_gl_against_bt_report_task(self):
        mail.outbox.clear()
        result = export_new_gl_against_bt_report_task(recipient_email="test-gl@example.com")
        self.assertIn("New GL Against BT Report containing 1 records sent to test-gl@example.com", result)
        self.assertEqual(len(mail.outbox), 1)

        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, "New GL Against BT Report")
        self.assertIn("Total New GL Against BT Records", sent_email.alternatives[0][0])
        self.assertEqual(len(sent_email.attachments), 1)

        attachment_name, attachment_content, content_type = sent_email.attachments[0]
        self.assertTrue(attachment_name.startswith("new_gl_against_bt_report_"))
        self.assertTrue(attachment_name.endswith(".xlsx"))

        # Verify Excel content
        excel_data = io.BytesIO(attachment_content)
        df = pd.read_excel(excel_data, engine="openpyxl")
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["FLID"], "APP-BT")
        self.assertEqual(df.iloc[0]["Exiting Bank"], "Exiting Bank Test")
        self.assertEqual(df.iloc[0]["New Bank"], "New Bank Test")
        self.assertEqual(df.iloc[0]["New Loan A/C"], "ACC123456")

    def test_export_tele_centre_report_task(self):
        import datetime
        from django.utils import timezone
        mail.outbox.clear()
        
        # Backdate the loan punch created_at to yesterday to make sure it's caught by the task
        yesterday = timezone.localtime(timezone.now()) - datetime.timedelta(days=1)
        LoanPunchV2.objects.filter(id=self.loan_punch.id).update(created_at=yesterday)
        
        result = export_tele_centre_report_task(recipient_email="test-tele@example.com")
        self.assertIn("Tele Centre Report containing 1 records sent to test-tele@example.com", result)
        self.assertEqual(len(mail.outbox), 1)

        sent_email = mail.outbox[0]
        self.assertTrue(sent_email.subject.startswith("Customer Details For Tele"))
        self.assertEqual(len(sent_email.attachments), 1)

        attachment_name, attachment_content, content_type = sent_email.attachments[0]
        self.assertTrue(attachment_name.startswith("Customer_Details_For_Tele_"))
        self.assertTrue(attachment_name.endswith(".xlsx"))

        # Verify Excel content
        excel_data = io.BytesIO(attachment_content)
        df = pd.read_excel(excel_data, engine="openpyxl")
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["Application ID"], "APP-BT")
        self.assertEqual(df.iloc[0]["Customer Name"], "John Doe")
        self.assertEqual(df.iloc[0]["Loan Account Number"], "ACC123456")
