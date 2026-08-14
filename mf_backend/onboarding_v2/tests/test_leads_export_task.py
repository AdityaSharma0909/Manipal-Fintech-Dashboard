from django.test import TestCase
from django.core import mail
from onboarding_v2.models import LeadV2
from onboarding_v2.constants import ProductSubCategory
from onboarding_v2.tasks import export_banca_leads_hourly_task
from django.contrib.auth import get_user_model

User = get_user_model()

class ExportLeadsTaskTests(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.user_banca = User.objects.create_user(
            username="banca_user",
            phone="+919876543210",
            role="LOAN_OFFICER",
            team="BANCA",
            employee_id="EMP001"
        )
        self.user_dst = User.objects.create_user(
            username="dst_user",
            phone="+919876543211",
            role="LOAN_OFFICER",
            team="DST",
            employee_id="EMP002"
        )

    def test_export_leads_filters_out_gold_loan_includes_all_teams(self) -> None:
        # 1. Gold Loan lead (created by BANCA user) - should be excluded
        LeadV2.objects.create(
            customer_name="Banca Gold Loan Lead",
            contact_number="1234567890",
            product_subcategory=ProductSubCategory.GOLD_LOAN,
            created_by=self.user_banca
        )

        # 2. Home Loan lead (created by BANCA user) - should be included
        LeadV2.objects.create(
            customer_name="Banca Home Loan Lead",
            contact_number="1234567891",
            product_subcategory=ProductSubCategory.HOME_LOAN,
            created_by=self.user_banca
        )

        # 3. Personal Loan lead (created by DST user) - should be included (BANCA team filter is removed!)
        LeadV2.objects.create(
            customer_name="DST Personal Loan Lead",
            contact_number="1234567892",
            product_subcategory=ProductSubCategory.PERSONAL_LOAN,
            created_by=self.user_dst
        )

        # Run the task
        result = export_banca_leads_hourly_task(recipient_email="test@example.com")

        # Verify output message and sent email
        self.assertIn("Report containing 2 leads successfully sent to test@example.com", result)
        self.assertEqual(len(mail.outbox), 1)
        
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.subject, "Non-GL Lead Report")
        self.assertIn("Total Leads: 2", sent_email.body)
        self.assertEqual(len(sent_email.attachments), 1)
        
        attachment_name, attachment_content, content_type = sent_email.attachments[0]
        self.assertTrue(attachment_name.startswith("non_gl_leads_report_"))
        self.assertTrue(attachment_name.endswith(".xlsx"))
