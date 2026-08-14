import os
import django
import uuid
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'radian_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection, transaction
from account.models import Account
from application.models import Application
from onboarding_v2.models import Packet, LeadV2, ApplicationV2
from loan.models import Loan
from branch.models import Branch

User = get_user_model()

def run_import():
    print("Step 1: Creating/Verifying dummy parent records...")
    
    # 1. Dummy User for payments/repayments
    system_user_id = '00000000-0000-0000-0000-000000000000'
    system_user, created = User.objects.get_or_create(
        user_id=system_user_id,
        defaults={
            'username': 'system_dummy',
            'phone': '+910000000000',
            'role': 'SUPER_ADMIN',
            'is_active': True,
            'is_staff': True,
            'is_superuser': True,
            'first_name': 'System',
            'last_name': 'Dummy',
            'email': 'system@example.com'
        }
    )
    if created:
        system_user.set_password('dummy_password')
        system_user.save()
        print(f"Created system user: {system_user_id}")
    else:
        print("System user already exists.")

    # 1b. Create the Axis Bank Lender to satisfy the FK dependency
    from lender.models import Lender
    axis_lender, created_lender = Lender.objects.get_or_create(
        lender_id='885e768f-5a5c-4459-a09d-ac433e2b4d11',
        defaults={
            'lender_name': 'AXIS BANK',
            'lender_code': 'AXIS',
            'lender_address': 'Mumbai, Maharashtra'
        }
    )
    if created_lender:
        print("Created Axis Bank lender.")
    else:
        print("Axis Bank lender already exists.")

    # Fix history sequence for Account before we get_or_create it
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT setval('account_historicalaccount_history_id_seq', COALESCE((SELECT MAX(history_id)+1 FROM account_historicalaccount), 1), false);")
            print("Successfully reset account_historicalaccount_history_id_seq.")
        except Exception as e:
            print("Failed to reset account history sequence:", e)

        try:
            cursor.execute("SELECT setval('application_historicalapplication_history_id_seq', COALESCE((SELECT MAX(history_id)+1 FROM application_historicalapplication), 1), false);")
            print("Successfully reset application_historicalapplication_history_id_seq.")
        except Exception as e:
            print("Failed to reset application history sequence:", e)

    # 2. Dummy Account for legacy Applications
    account, created = Account.objects.get_or_create(
        account_id='00000000-0000-0000-0000-000000000000',
        defaults={
            'customer_id': 'DUMMYCUST',
            'email': 'dummy@example.com',
            'gender': 'Male',
            'year_of_birth': timezone.now(),
            'net_annual_income': 0,
            'mother_name': 'Dummy Mother',
            'father_name': 'Dummy Father',
            'user': system_user,
            'created_by': system_user,
        }
    )
    if created:
        print("Created dummy account.")
    else:
        print("Dummy account already exists.")

    # 3. Dummy legacy Applications to satisfy loan_loan foreign keys
    apps_to_create = [
        ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b11', 'APP-2025-001'),
        ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b12', 'APP-2025-002'),
        ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b13', 'APP-2025-003'),
        ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b15', 'APP-2025-005'),
    ]
    for app_id, app_num in apps_to_create:
        app, created = Application.objects.get_or_create(
            application_id=app_id,
            defaults={
                'account': account,
                'application_number': app_num,
                'status': 'NEW_APPLICATION',
            }
        )
        if created:
            print(f"Created legacy application: {app_id} ({app_num})")

    # 4. Clean up any existing records matching the synthetic dataset to ensure re-runnability (idempotency)
    print("Step 2: Cleaning up existing synthetic records to avoid primary key conflicts...")
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM public.payment_repayment WHERE repayment_id IN ('f5eebc99-9c0b-4ef8-bb6d-6bb9bd380f11', 'f5eebc99-9c0b-4ef8-bb6d-6bb9bd380f12', 'f5eebc99-9c0b-4ef8-bb6d-6bb9bd380f13');")
        cursor.execute("DELETE FROM public.disbursements_disbursement WHERE disbursement_id IN ('e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e11', 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e12', 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e13', 'e4eebc99-9c0b-4ef8-bb6d-6bb9bd380e15');")
        cursor.execute("DELETE FROM public.loan_loan WHERE loan_id IN ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380d11', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d12', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d13', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d15');")
        cursor.execute("DELETE FROM public.onboarding_v2_jewelleryitem WHERE id IN ('c2eebc99-9c0b-4ef8-bb6d-6bb9bd380c11', 'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380c12', 'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380c13', 'c2eebc99-9c0b-4ef8-bb6d-6bb9bd380c15');")
        cursor.execute("DELETE FROM public.onboarding_v2_packet WHERE id IN ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b11', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b12', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b13', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b15');")
        cursor.execute("DELETE FROM public.onboarding_v2_applicationv2 WHERE id IN ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b11', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b12', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b13', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b14', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b15');")
        cursor.execute("DELETE FROM public.onboarding_v2_leadv2 WHERE id IN ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a14', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15');")

    # 5. Execute SQL script with disabled triggers for jewellery items
    print("Step 3: Executing synthetic dataset SQL script...")
    sql_path = os.path.join(os.path.dirname(__file__), 'synthetic_nbfc_dashboard_data.sql')
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    with connection.cursor() as cursor:
        print("Disabling constraint checks on onboarding_v2_jewelleryitem...")
        cursor.execute("ALTER TABLE public.onboarding_v2_jewelleryitem DISABLE TRIGGER ALL;")
        try:
            cursor.execute(sql_content)
            print("SQL script executed.")
        finally:
            # We must restore triggers later, but first we create Packets to satisfy the constraint!
            pass

    # 6. Create V2 packets now that onboarding_v2_applicationv2 rows are inserted!
    print("Step 4: Seeding V2 Packets to satisfy jewellery constraint...")
    packets_data = [
        ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b11', 'PKT-1001', 50.00, 325000.00, 47.00, 305500.00),
        ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b12', 'PKT-1002', 100.00, 650000.00, 93.00, 604500.00),
        ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b13', 'PKT-1003', 25.00, 150000.00, 23.50, 141000.00),
        ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b15', 'PKT-1005', 150.00, 975000.00, 147.00, 955500.00),
    ]
    for app_id, pkt_num, gross_w, gross_val, net_w, net_val in packets_data:
        Packet.objects.create(
            id=app_id, # matching packet_id in jewellery inserts
            application_id=app_id,
            packet_id=pkt_num,
            gross_weight=gross_w,
            gross_value=gross_val,
            net_adjusted_weight=net_w,
            net_adjusted_value=net_val,
            metadata={}
        )
        print(f"Created V2 Packet: {pkt_num}")

    # Re-enable constraint checks
    with connection.cursor() as cursor:
        print("Re-enabling constraint checks on onboarding_v2_jewelleryitem...")
        cursor.execute("ALTER TABLE public.onboarding_v2_jewelleryitem ENABLE TRIGGER ALL;")

    # 7. Post-import updates for dashboard mapping
    print("Step 5: Performing post-import updates...")
    
    # Map loans to AXIS BANK lender ('885e768f-5a5c-4459-a09d-ac433e2b4d11') so they appear in lender stats
    with connection.cursor() as cursor:
        cursor.execute("UPDATE public.loan_loan SET lender_id = '885e768f-5a5c-4459-a09d-ac433e2b4d11' WHERE loan_id IN ('d3eebc99-9c0b-4ef8-bb6d-6bb9bd380d11', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d12', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d13', 'd3eebc99-9c0b-4ef8-bb6d-6bb9bd380d15');")
        print("Mapped synthetic loans to Axis Bank.")

    # Assign leads to a real Sales Officer (superuser admin: 'f19bfcd5-883c-46dd-a64a-a6385be19ed8')
    with connection.cursor() as cursor:
        cursor.execute("UPDATE public.onboarding_v2_leadv2 SET assigned_to_id = 'f19bfcd5-883c-46dd-a64a-a6385be19ed8' WHERE id IN ('a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a12', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a13', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a15');")
        print("Assigned synthetic leads to admin user.")

    # Assign applications to a real Regional Head (QARHuser: '652a9a3a-948e-4582-b741-50be737695c6')
    with connection.cursor() as cursor:
        cursor.execute("UPDATE public.onboarding_v2_applicationv2 SET punched_by_id = 'f19bfcd5-883c-46dd-a64a-a6385be19ed8', assigned_rh_id = '652a9a3a-948e-4582-b741-50be737695c6' WHERE id IN ('b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b11', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b12', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b13', 'b1eebc99-9c0b-4ef8-bb6d-6bb9bd380b15');")
        print("Assigned synthetic applications to admin (punched_by) and QARHuser (assigned_rh).")

    print("Data import complete!")

if __name__ == '__main__':
    run_import()
