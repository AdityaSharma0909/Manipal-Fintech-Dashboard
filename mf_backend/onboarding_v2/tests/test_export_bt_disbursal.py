import io
import pandas as pd
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from onboarding_v2.constants import LeadType
from onboarding_v2.models import (
    ApplicationV2,
    LeadV2,
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
class ExportBTDisbursalReportViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="agent",
            password="pass",
            phone="9000000000",
            role="LOAN_OFFICER",
            employee_id="EMP001",
        )
        self.client.force_authenticate(user=self.user)

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

    def test_export_includes_van_number(self):
        response = self.client.get("/api/v2/onboarding/applications/export/bt-disbursal/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # Parse output excel sheet
        excel_data = io.BytesIO(response.content)
        df = pd.read_excel(excel_data, engine="openpyxl")

        # Verify "VAN Number" column exists
        self.assertIn("VAN Number", df.columns)

        # Verify the record values
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["FLID"], "APP-BT")
        self.assertEqual(df.iloc[0]["VAN Number"], "VAN-TEST-12345")
