import io
import datetime
import pandas as pd
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone

from onboarding_v2.constants import LeadType
from onboarding_v2.models import (
    ApplicationV2,
    LeadV2,
    LoanPunchV2,
    ApplicationStageSnapshot,
    PincodeMaster,
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
class ExportTeleCentreReportViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="agent",
            password="pass",
            phone="9000000000",
            role="SUPER_ADMIN",
            employee_id="EMP001",
        )
        self.client.force_authenticate(user=self.user)

        # Create Lead
        self.lead = LeadV2.objects.create(
            customer_id="CUST-TC",
            contact_number="9876543210",
            customer_name="Jane Doe",
            product_category="LOAN",
            assigned_to=self.user,
            lead_type="FRESH",
            pincode="400001",
            gender="FEMALE",
            dob=datetime.date(1990, 5, 20),
            created_by=self.user,
        )

        # Create Application
        self.app = ApplicationV2.objects.create(
            application_id="APP-TC",
            lead=self.lead,
            loan_type=LeadType.FRESH,
            lending_partner="AXIS_BANK",
            partner_branch_name="Mumbai Main",
            applicant_profession="SALARIED",
        )

        # Create stage snapshots
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage="BASIC",
            payload={
                "profession": "SALARIED",
                "qualification": "GRADUATE",
                "dob": "1990-05-20",
                "gender": "FEMALE",
                "father_full_name": "Father Doe",
            }
        )
        ApplicationStageSnapshot.objects.create(
            application=self.app,
            stage="ADDRESS",
            payload={
                "permanent": {
                    "district": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400001",
                }
            }
        )

        # Create PincodeMaster
        PincodeMaster.objects.create(
            pincode="400001",
            district="Mumbai",
            statename="Maharashtra",
        )

        # Create LoanPunchV2 (yesterday to match defaults)
        self.loan_punch = LoanPunchV2.objects.create(
            application=self.app,
            bank_name="AXIS_BANK",
            loan_account_number="ACT-TC-123",
            disbursed_amount=75000.00,
            rate_of_interest=10.25,
            loan_opening_date=datetime.date(2026, 7, 29),
        )
        # Backdate the loan punch created_at to yesterday
        yesterday = timezone.localtime(timezone.now()) - datetime.timedelta(days=1)
        LoanPunchV2.objects.filter(id=self.loan_punch.id).update(created_at=yesterday)

    def test_export_tele_centre_report_defaults_to_yesterday(self):
        response = self.client.get("/api/v2/onboarding/applications/export/tele-centre-report/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Parse Excel content
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data, engine="openpyxl")

        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["Application ID"], "APP-TC")
        self.assertEqual(df.iloc[0]["Customer Name"], "Jane Doe")
        self.assertEqual(df.iloc[0]["Loan Account Number"], "ACT-TC-123")
        self.assertEqual(df.iloc[0]["Loan Amount"], 75000.00)
        self.assertEqual(df.iloc[0]["ROI"], 10.25)
        self.assertEqual(df.iloc[0]["State"], "Maharashtra")
        self.assertEqual(df.iloc[0]["Zone"], "West")

    def test_export_tele_centre_report_custom_date_range(self):
        # Update loan punch to be created today
        today = timezone.localtime(timezone.now())
        LoanPunchV2.objects.filter(id=self.loan_punch.id).update(created_at=today)

        # Query yesterday (should be empty)
        yesterday_str = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.client.get(
            f"/api/v2/onboarding/applications/export/tele-centre-report/?start_date={yesterday_str}&end_date={yesterday_str}"
        )
        self.assertEqual(response.status_code, 200)
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data, engine="openpyxl")
        self.assertEqual(len(df), 0)

        # Query today (should have 1 record)
        today_str = today.strftime("%Y-%m-%d")
        response = self.client.get(
            f"/api/v2/onboarding/applications/export/tele-centre-report/?start_date={today_str}&end_date={today_str}"
        )
        self.assertEqual(response.status_code, 200)
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data, engine="openpyxl")
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["Application ID"], "APP-TC")
