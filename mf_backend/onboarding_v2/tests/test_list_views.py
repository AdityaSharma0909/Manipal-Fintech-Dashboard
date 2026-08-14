from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from users.models import User

from onboarding_v2.constants import ApplicationStage
from onboarding_v2.models import (
    ApplicationStageSnapshot,
    ApplicationV2,
    LendingPartnerMaster,
    LeadV2,
    LoanPunchV2,
    PincodeMaster,
)


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class ListViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="agent", password="pass", phone="9000000000")
        self.other = User.objects.create_user(username="other", password="pass", phone="9000000001")
        self.client.force_authenticate(user=self.user)

        lead_assigned = LeadV2.objects.create(
            customer_id="CUST-A",
            contact_number="9000000000",
            customer_name="Lead A",
            product_category="LOAN",
            assigned_to=self.user,
        )
        LeadV2.objects.create(
            customer_id="CUST-B",
            contact_number="8000000000",
            customer_name="Lead B",
            product_category="LOAN",
            assigned_to=self.other,
        )
        ApplicationV2.objects.create(application_id="APP-A", lead=lead_assigned)
        lead_other = LeadV2.objects.create(
            customer_id="CUST-C",
            contact_number="7000000000",
            customer_name="Lead C",
            product_category="LOAN",
            assigned_to=self.other,
        )
        ApplicationV2.objects.create(application_id="APP-B", lead=lead_other)

    def test_lead_list_filters_by_agent(self):
        resp = self.client.get("/api/v2/onboarding/leads/list/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["data"]["results"]
        # paginated response with "results" and "leads" inside
        leads = data["leads"]
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["customer_id"], "CUST-A")

    def test_application_list_filters_by_agent(self):
        resp = self.client.get("/api/v2/onboarding/applications/list/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        apps = data["applications"]
        self.assertEqual(len(apps), 1)
        self.assertEqual(apps[0]["application_id"], "APP-A")

    def test_application_list_payload_fields(self):
        lead = LeadV2.objects.create(
            customer_id="CUST-D",
            contact_number="9000001111",
            customer_name="Lead D",
            product_category="LOAN",
            product_subcategory="GOLD_LOAN",
            lead_type="FRESH",
            amount="150000",
            assigned_to=self.user,
        )
        app = ApplicationV2.objects.create(
            application_id="APP-D",
            lead=lead,
            loan_type="BT",
            partner_branch_name="Main Branch",
        )
        ApplicationStageSnapshot.objects.create(
            application=app,
            stage=ApplicationStage.ADDRESS,
            payload={
                "permanent": {"pincode": "560001"},
                "current": {},
            },
        )
        PincodeMaster.objects.create(
            pincode="560001",
            district="BENGALURU URBAN",
            statename="KARNATAKA",
        )

        resp = self.client.get("/api/v2/onboarding/applications/list/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]["applications"]
        app_row = next(item for item in data if item["application_id"] == "APP-D")
        self.assertEqual(app_row["name"], "Lead D")
        self.assertEqual(app_row["customer_id"], "CUST-D")
        self.assertEqual(app_row["loan_type"], "BT")
        self.assertEqual(app_row["lead_type"], "FRESH")
        self.assertEqual(app_row["product_category"], "LOAN")
        self.assertEqual(app_row["product_subcategory"], "GOLD_LOAN")
        self.assertEqual(app_row["mobile_number"], "9000001111")
        self.assertEqual(app_row["pincode"], "560001")
        self.assertEqual(app_row["state"], "KARNATAKA")
        self.assertEqual(app_row["district"], "BENGALURU URBAN")
        self.assertEqual(app_row["bank_branch"], "Main Branch")

    def test_application_list_includes_total_disbursed_amount_from_loan_punches(self):
        app = ApplicationV2.objects.get(application_id="APP-A")
        LoanPunchV2.objects.create(
            application=app,
            bank_name="Test Bank",
            disbursed_amount="100000.50",
        )
        LoanPunchV2.objects.create(
            application=app,
            bank_name="Test Bank",
            disbursed_amount="25000.25",
        )

        resp = self.client.get("/api/v2/onboarding/applications/list/")

        self.assertEqual(resp.status_code, 200)
        app_row = resp.json()["results"]["applications"][0]
        self.assertEqual(app_row["disbursed_amount"], "125000.75")

    def test_lending_partner_create_and_list(self):
        create_resp = self.client.post(
            "/api/v2/onboarding/lending-partners/",
            data={
                "bank_name": "Axis Bank",
                "available_for": "GOLD_LOAN",
                "available_for_lead_type": [
                    "CO_LENDING",
                    "FRESH",
                    "BALANCE_TRANSFER",
                    "SELF_LENDING",
                ],
            },
        )
        self.assertEqual(create_resp.status_code, 200)
        self.assertEqual(LendingPartnerMaster.objects.count(), 1)

        list_resp = self.client.get(
            "/api/v2/onboarding/lending-partners/",
            {"available_for": "GOLD_LOAN"},
        )
        self.assertEqual(list_resp.status_code, 200)
        payload = list_resp.json()["data"]
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["bank_name"], "Axis Bank")
        self.assertEqual(payload["results"][0]["available_for"], "GOLD_LOAN")
        self.assertEqual(
            payload["results"][0]["available_for_lead_type"],
            ["CO_LENDING", "FRESH", "BALANCE_TRANSFER", "SELF_LENDING"],
        )

    def test_lead_list_filters_by_lead_type(self):
        # Create lead with BANK_LEAD
        LeadV2.objects.create(
            customer_id="CUST-BANK",
            contact_number="9000000002",
            customer_name="Bank Lead A",
            product_category="LOAN",
            lead_type="BANK_LEAD",
            assigned_to=self.user,
        )
        # Create lead with FRESH
        LeadV2.objects.create(
            customer_id="CUST-FRESH",
            contact_number="9000000003",
            customer_name="Fresh Lead B",
            product_category="LOAN",
            lead_type="FRESH",
            assigned_to=self.user,
        )
        
        # Filter by BANK_LEAD
        resp = self.client.get("/api/v2/onboarding/leads/list/", {"lead_type": "BANK_LEAD"})
        self.assertEqual(resp.status_code, 200)
        leads = resp.json()["data"]["results"]["leads"]
        self.assertTrue(all(l["lead_type"] == "BANK_LEAD" for l in leads))
        self.assertTrue(any(l["customer_id"] == "CUST-BANK" for l in leads))
        self.assertFalse(any(l["customer_id"] == "CUST-FRESH" for l in leads))

    def test_application_list_filters_by_lead_type(self):
        lead_bank = LeadV2.objects.create(
            customer_id="CUST-BANK-APP",
            contact_number="9000000004",
            customer_name="Bank Lead C",
            product_category="LOAN",
            lead_type="BANK_LEAD",
            assigned_to=self.user,
        )
        ApplicationV2.objects.create(application_id="APP-BANK", lead=lead_bank)

        lead_fresh = LeadV2.objects.create(
            customer_id="CUST-FRESH-APP",
            contact_number="9000000005",
            customer_name="Fresh Lead D",
            product_category="LOAN",
            lead_type="FRESH",
            assigned_to=self.user,
        )
        ApplicationV2.objects.create(application_id="APP-FRESH", lead=lead_fresh)

        # Filter by BANK_LEAD
        resp = self.client.get("/api/v2/onboarding/applications/list/", {"lead_type": "BANK_LEAD"})
        self.assertEqual(resp.status_code, 200)
        apps = resp.json()["results"]["applications"]
        self.assertTrue(all(a["lead_type"] == "BANK_LEAD" for a in apps))
        self.assertTrue(any(a["application_id"] == "APP-BANK" for a in apps))
        self.assertFalse(any(a["application_id"] == "APP-FRESH" for a in apps))
