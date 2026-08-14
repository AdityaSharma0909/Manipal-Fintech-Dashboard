import os
import django
import random
import uuid
from datetime import datetime, timedelta, date

# Setup django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "radian_backend.settings")
django.setup()

from django.utils import timezone
from users.models import User
from branch.models import Branch
from lender.models import Lender
from lead.models import Lead, NewLead
from account.models import Account
from application.models import Application
from loan.models import Loan
from onboarding_v2.models import Customers

def seed():
    print("Starting seeding process...")
    
    # 1. Clean up existing data to avoid duplicates/conflicts
    print("Cleaning up old data...")
    Loan.objects.all().delete()
    Application.objects.all().delete()
    Account.objects.all().delete()
    NewLead.objects.all().delete()
    Lead.objects.all().delete()
    Branch.objects.all().delete()
    Lender.objects.all().delete()
    
    # Get available users
    users = list(User.objects.all())
    if not users:
        print("Error: No users found in users_user table. Please ensure migrations/dumps are loaded.")
        return
    print(f"Found {len(users)} users in database.")
    
    # Select some sales officers and branch managers
    officers = [u for u in users if u.role == 'SALES_OFFICER']
    if not officers:
        officers = users[:5] # fallback
    bms = [u for u in users if u.role == 'SUPER_ADMIN' or u.role == 'REGIONAL_HEAD']
    if not bms:
        bms = users[:2] # fallback
        
    print(f"Selected {len(officers)} officers and {len(bms)} managers for attributes.")

    # 2. Create Lenders
    print("Creating Lenders...")
    lenders = []
    lender_data = [
        ("ICICI BANK", "ICICI", "Mumbai, Maharashtra"),
        ("AXIS BANK", "AXIS", "Mumbai, Maharashtra"),
        ("FEDERAL BANK", "FEDERAL", "Kochi, Kerala"),
    ]
    for name, code, addr in lender_data:
        l = Lender.objects.create(
            lender_name=name,
            lender_code=code,
            lender_address=addr
        )
        lenders.append(l)
        print(f" - Created Lender: {name}")

    # 3. Create Branches
    print("Creating Branches...")
    branches = []
    branch_data = [
        ("BLR01", "Bangalore Central", "Karnataka", 12.9716, 77.5946),
        ("BOM01", "Mumbai South", "Maharashtra", 19.0760, 72.8777),
        ("DEL01", "Delhi Connaught Place", "Delhi", 28.6139, 77.2090),
        ("MAA01", "Chennai T-Nagar", "Tamil Nadu", 13.0827, 80.2707),
        ("HYD01", "Hyderabad Gachibowli", "Telangana", 17.3850, 78.4867),
    ]
    for code, name, state, lat, lng in branch_data:
        b = Branch.objects.create(
            branch_code=code,
            branch_name=name,
            state=state,
            latitude=lat,
            longitude=lng,
            phone="9876543210",
            email=f"{code.lower()}@manipalfintech.com",
            address=f"Manipal Fintech Office, {name}, {state}",
            opening_date=date.today() - timedelta(days=365)
        )
        branches.append(b)
        print(f" - Created Branch: {name}")

    # Helper function to generate a random date in the last 180 days
    def random_past_date(days_back=180):
        seconds_back = random.randint(0, days_back * 24 * 3600)
        dt = timezone.now() - timedelta(seconds=seconds_back)
        return dt

    # 4. Create Classic Leads
    print("Creating Classic Leads...")
    lead_sources = ["WALK_IN", "PARTNER_PORTAL", "WEBSITE", "DIRECT_MARKETING", "TELE_CALLING"]
    lending_types = ["Gold Loan", "Business Loan", "Home Loan", "Personal Loan"]
    lead_statuses = ["NEW", "CONTACTED", "INTERESTED", "CONVERTED", "CLOSED_LOST"]
    
    first_names = ["Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Siddharth", "Neha", "Arjun", "Aditi"]
    last_names = ["Sharma", "Verma", "Gupta", "Singh", "Patel", "Reddy", "Nair", "Joshi", "Rao", "Kumar"]
    
    for i in range(150):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        assigned_to = random.choice(officers)
        created_at = random_past_date()
        
        Lead.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone=f"9{random.randint(100000000, 999999999)}",
            comments="Interested in taking a quick mortgage loan for business expansion.",
            status=random.choice(lead_statuses),
            created_at=created_at,
            assigned_to=assigned_to,
            source=random.choice(lead_sources),
            lending_type=random.choice(lending_types),
            dob=date(1980 + random.randint(0, 20), random.randint(1, 12), random.randint(1, 28))
        )
    print("Generated 150 Classic Leads.")

    # 5. Create External Leads (NewLead)
    print("Creating External Leads...")
    new_lead_types = ["MICRO_LOAN", "LAP", "PERSONAL_LOAN", "SME_LOAN"]
    new_lead_statuses = ["NEW", "UNDER_REVIEW", "APPROVED", "DISBURSED", "REJECTED"]
    for i in range(100):
        created_at = random_past_date()
        NewLead.objects.create(
            created_at=created_at,
            status=random.choice(new_lead_statuses),
            loan_type=random.choice(new_lead_types),
            lead_id=f"EXT-L-{uuid.uuid4().hex[:12]}"
        )
    print("Generated 100 External Leads.")

    # 6. Create Accounts (Mandatory dependency for Applications)
    print("Creating Accounts...")
    accounts = []
    customers = list(Customers.objects.all())
    for idx, customer in enumerate(customers[:100]):
        user = random.choice(officers)
        branch = random.choice(branches)
        acc = Account.objects.create(
            customer_id=f"CUST-{idx:05d}",
            user=user,
            created_by=user,
            branch=branch,
            year_of_birth=timezone.now() - timedelta(days=365 * random.randint(20, 50)),
            gender=random.choice(["MALE", "FEMALE"]),
            status="ACTIVE",
            aadhar_verified=True,
            pan_verified=True,
            net_annual_income=random.randint(300000, 1500000),
            pan_no=f"PAN{idx:05d}K",
            aadhar_no=f"9{idx:011d}"
        )
        accounts.append(acc)
    print(f"Generated {len(accounts)} Accounts.")

    # 7. Create Applications
    print("Creating Applications...")
    app_loan_types = ["Gold Loan", "SME Loan", "LAP", "Personal Loan"]
    app_statuses = [
        "NEW_APPLICATION", "ASSET_ADDED", "CREDIT_STATUS_CHECKED", 
        "UNDERWRITING_APPROVED", "PAYMENT_DETAILS_RECORDED", "REJECTED"
    ]
    
    for i in range(120):
        branch = random.choice(branches)
        lender = random.choice(lenders)
        officer = random.choice(officers)
        bm = random.choice(bms)
        account = random.choice(accounts)
        created_at = random_past_date()
        
        loan_amount = random.randint(50000, 1500000)
        
        Application.objects.create(
            status=random.choice(app_statuses),
            application_number=f"APP-{random.randint(1000000, 9999999)}",
            purpose_of_loan="Gold assets monetization / working capital",
            eligible_amount=loan_amount,
            loan_amount=loan_amount,
            disbursed_amount=loan_amount if random.choice([True, False]) else 0,
            tenure=random.choice([6, 12, 24, 36]),
            intrest_rate=random.choice([11.5, 12.0, 14.5, 18.0]),
            created_at=created_at,
            modefied_at=created_at + timedelta(days=random.randint(1, 10)),
            Originatedby=officer,
            approvedByBM=bm,
            lender=lender,
            branch=branch,
            account=account,
            application_loan_type=random.choice(app_loan_types),
            processing_fee=random.randint(1000, 5000),
            current_gst_rate=18.0,
            gst=random.randint(180, 900),
            stamp_duty=random.randint(100, 500),
            penalty=0.0
        )
    print("Generated 120 Applications.")

    # 8. Create Loans
    print("Creating Loans...")
    # Select applications that reached disbursed/payment recorded stage
    disbursed_apps = list(Application.objects.filter(status="PAYMENT_DETAILS_RECORDED"))
    
    for idx, app in enumerate(disbursed_apps):
        dpd_options = [0, 0, 0, 15, 30, 45, 95, 120] # DPD values
        dpd = random.choice(dpd_options)
        
        if dpd > 90:
            loan_status = "Active - Bad Standing"
        elif dpd > 0:
            loan_status = "Active - Bad Standing"
        else:
            loan_status = "Active - Good Standing"
            
        principal_rem = float(app.loan_amount) * random.uniform(0.3, 0.95)
        interest_rem = principal_rem * 0.05
        
        Loan.objects.create(
            loan_number=f"LN-{app.application_number.split('-')[1]}",
            application=app,
            status=loan_status,
            term=app.tenure,
            intrest_rate=app.intrest_rate,
            tenure=app.tenure,
            lender=app.lender,
            loan_amount=app.loan_amount,
            loan_type=app.application_loan_type,
            days_past_dues=dpd,
            current_amount=app.loan_amount,
            purpose_of_loan=app.purpose_of_loan,
            eligible_amount=app.eligible_amount,
            branch=app.branch,
            approvedByBM=app.approvedByBM,
            approvedByBMAt=app.created_at + timedelta(days=2),
            disbursed_amount=app.loan_amount,
            disbursed_date=app.created_at + timedelta(days=3),
            due_date=app.created_at + timedelta(days=30),
            disbursal_amount=app.loan_amount,
            net_disbursed_amount=app.loan_amount,
            current_emi=float(app.loan_amount) / app.tenure,
            interest_accrued_till_date=float(app.loan_amount) * 0.08,
            principal_paid=float(app.loan_amount) - principal_rem,
            interest_paid=float(app.loan_amount) * 0.04,
            penalty_paid=0.0,
            principal_remaining=principal_rem,
            interest_remaining=interest_rem,
            next_due_date=timezone.now() + timedelta(days=random.randint(-15, 15))
        )
    print(f"Generated {len(disbursed_apps)} Loans from applications.")
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed()
