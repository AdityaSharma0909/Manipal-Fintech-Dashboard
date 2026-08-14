from __future__ import annotations

from datetime import datetime
from typing import Optional

from django.db import IntegrityError, transaction
from django.db.models import Q

from onboarding_v2.constants import (
    ApplicationStage,
    ApplicationStatus,
    LeadStatus,
    LeadType,
)
from onboarding_v2.models import ApplicationV2, LeadV2, PincodeMaster
from onboarding_v2.serializers import ApplicationCreateSerializer, LeadCreateSerializer
from onboarding_v2.services import (
    generate_application_id,
    generate_customer_id,
    generate_lead_code,
    resolve_pre_screen_completion,
    resolve_post_screen_completion,
)


def prepare_lead_create_data(user, data: dict) -> dict:
    payload = data.copy()
    # Use pk to support custom user PK (user_id)
    payload["created_by"] = getattr(user, "pk", None)
    payload["modified_by"] = getattr(user, "pk", None)
    # auto-assign lead to the creator (agent) so it doesn't stay unassigned
    payload["assigned_to"] = getattr(user, "pk", None)
    # payload["customer_id"] = generate_customer_id()  # Deferred to PAN verification
    payload["lead_code"] = generate_lead_code(
        payload.get("product_category"),
        payload.get("product_subcategory"),
        payload.get("loan_type"),
    )
    # payload["status"] = ApplicationStatus.NEW_LEAD
    return payload


def create_lead(payload: dict) -> LeadV2:
    serializer = LeadCreateSerializer(data=payload)
    if not serializer.is_valid():
        raise ValueError(serializer.errors)

    def _apply_audit_fields(lead: LeadV2, data: dict) -> LeadV2:
        created_by_id = data.get("created_by")
        modified_by_id = data.get("modified_by")
        assigned_to_id = data.get("assigned_to")
        update_fields = []
        if created_by_id and lead.created_by_id != created_by_id:
            lead.created_by_id = created_by_id
            update_fields.append("created_by")
        if modified_by_id and lead.modified_by_id != modified_by_id:
            lead.modified_by_id = modified_by_id
            update_fields.append("modified_by")
        if assigned_to_id and lead.assigned_to_id != assigned_to_id:
            lead.assigned_to_id = assigned_to_id
            update_fields.append("assigned_to")
        if update_fields:
            lead.save(update_fields=update_fields)
        return lead

    # Attempt save; if customer_id collides, regenerate once and retry.
    try:
        with transaction.atomic():
            lead = serializer.save()
            return _apply_audit_fields(lead, payload)
    except IntegrityError as exc:
        msg = str(exc)
        if "customer_id" in msg:
            # Should not happen if customer_id is null initially
            raise ValueError("Customer ID collision occurred unexpectedly.")
        if "lead_code" in msg:
            # regenerate once and retry
            payload = payload.copy()
            payload["lead_code"] = generate_lead_code(
                payload.get("product_category"),
                payload.get("product_subcategory"),
                payload.get("loan_type"),
            )
            serializer = LeadCreateSerializer(data=payload)
            if not serializer.is_valid():
                raise ValueError(serializer.errors)
            try:
                with transaction.atomic():
                    lead = serializer.save()
                    return _apply_audit_fields(lead, payload)
            except IntegrityError:
                raise ValueError("Generated lead_code collided. Please retry.")
        raise RuntimeError("Failed to create lead.")


def filter_leads(user, params, all_users=False):
    from users.models import User
    from utils.constants import ROLES

    if all_users or user.role in (ROLES.SUPER_ADMIN.value, ROLES.VERTICAL_ADMIN.value, ROLES.CPC.value):
        qs = LeadV2.objects.all()
    elif user.role == ROLES.SALES_OFFICER.value:
        agent_ids = list(User.objects.filter(assign_so=user).values_list('user_id', flat=True))
        agent_ids.append(user.user_id)
        qs = LeadV2.objects.filter(Q(assigned_to_id__in=agent_ids) | Q(created_by_id__in=agent_ids))
    elif user.role == ROLES.REGIONAL_HEAD.value:
        # RH can see leads of assigned SOs and their agents
        # 1. Direct reportees (SOs or Agents directly assigned to RH)
        direct_ids = list(User.objects.filter(assign_so=user).values_list('user_id', flat=True))
        # 2. Indirect reportees (Agents assigned to those SOs)
        indirect_ids = list(User.objects.filter(assign_so_id__in=direct_ids).values_list('user_id', flat=True))
        managed_user_ids = list(set(direct_ids + indirect_ids + [user.user_id]))
        qs = LeadV2.objects.filter(Q(assigned_to_id__in=managed_user_ids) | Q(created_by_id__in=managed_user_ids))
    elif user.role == ROLES.TELE_ADMIN.value:
        team_ids = [user.user_id]
        if getattr(user, 'team', None):
            team_ids = list(User.objects.filter(team=user.team).values_list('user_id', flat=True))
        qs = LeadV2.objects.filter(Q(assigned_to_id__in=team_ids) | Q(created_by_id__in=team_ids))
    else:
        qs = LeadV2.objects.filter(Q(assigned_to=user) | Q(created_by=user))

    qs = qs.order_by("-created_at")
    
    # Exclude unverified leads by default
    qs = qs.exclude(status=LeadStatus.UNVERIFIED)

    # Search (General)
    search = params.get("search")
    if search:
        qs = qs.filter(
            Q(lead_code__icontains=search) |
            Q(contact_number__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(pan_number__icontains=search)
        )

    # Specific Search/Filters
    lead_code = params.get("lead_code") or params.get("lead_id")
    if lead_code:
        qs = qs.filter(lead_code__iexact=lead_code)
        
    contact_number = params.get("contact_number") or params.get("phone")
    if contact_number:
        qs = qs.filter(contact_number__icontains=contact_number)
        
    customer_name = params.get("customer_name") or params.get("full_name")
    if customer_name:
        qs = qs.filter(customer_name__icontains=customer_name)

    customer_id = params.get("customer_id")
    if customer_id:
        qs = qs.filter(customer_id__icontains=customer_id)

    # Product
    product_category = params.get("product_category")
    if product_category:
        qs = qs.filter(product_category__iexact=product_category)
    product_subcategory = params.get("product_subcategory") or params.get("loan_type")
    if product_subcategory:
        subcats = [s.strip() for s in product_subcategory.split(",") if s.strip()]
        if subcats:
            qs = qs.filter(product_subcategory__in=subcats)

    # Pincode, District, State
    pincode = params.get("pincode")
    if pincode:
        qs = qs.filter(pincode__icontains=pincode)
    
    district = params.get("district")
    state = params.get("state")
    if district or state:
        pincode_qs = PincodeMaster.objects.all()
        if district:
            districts = [d.strip() for d in district.split(",") if d.strip()]
            dist_q = Q()
            for d in districts:
                dist_q |= Q(district__icontains=d)
            pincode_qs = pincode_qs.filter(dist_q)
        if state:
            states = [s.strip() for s in state.split(",") if s.strip()]
            state_q = Q()
            for s in states:
                state_q |= Q(statename__icontains=s)
            pincode_qs = pincode_qs.filter(state_q)
        matching_pincodes = pincode_qs.values_list('pincode', flat=True)
        qs = qs.filter(pincode__in=matching_pincodes)

    # Punched by (employee_id)
    punched_by = params.get("punched_by")
    if punched_by:
        qs = qs.filter(created_by__employee_id__iexact=punched_by)

    # Manager ID
    manager_id = params.get("manager_id")
    if manager_id:
        manager_id = str(manager_id).strip()
        manager_q = Q(created_by__assign_so__employee_id__iexact=manager_id) | Q(assigned_to__assign_so__employee_id__iexact=manager_id)
        
        # Only add UUID filters if it's a valid UUID
        import uuid
        try:
            uuid.UUID(manager_id)
            manager_q |= Q(created_by__assign_so_id=manager_id) | Q(assigned_to__assign_so_id=manager_id)
        except ValueError:
            pass
            
        qs = qs.filter(manager_q)

    # Lending Partner
    lending_partner = params.get("lending_partner") or params.get("bank")
    if lending_partner:
        partners = [p.strip() for p in lending_partner.split(",") if p.strip()]
        if partners:
            qs = qs.filter(
                Q(lending_partner__in=partners) |
                Q(applications__lending_partner__in=partners)
            ).distinct()


    # Lead Type
    lead_type = params.get("lead_type")
    if lead_type:
        lead_types = [lt.strip() for lt in lead_type.split(",") if lt.strip()]
        if lead_types:
            qs = qs.filter(lead_type__in=[lt.upper() for lt in lead_types])

    # Source
    source = params.get("source")
    if source and source not in ["MoneyPal", "FINCOME"]:
        qs = qs.filter(source__iexact=source)

    # Status Mapping (Swati's comments)
    status = params.get("status")
    if status:
        status_list = [s.strip() for s in status.split(",") if s.strip()]
        mapped_statuses = []
        for s in status_list:
            if s.lower() == "active":
                mapped_statuses.append(LeadStatus.ACTIVE)
            elif s.lower() == "auto close":
                mapped_statuses.append(LeadStatus.AUTO_CLOSED)
            elif s.lower() == "application created":
                mapped_statuses.append(LeadStatus.APPLICATION_CREATED)
            else:
                mapped_statuses.append(s)
        
        if mapped_statuses:
            qs = qs.filter(status__in=mapped_statuses)

    # Date Filter
    created_on = params.get("created_on") # YYYY-MM-DD
    if created_on:
        qs = qs.filter(created_at__date=created_on)
    
    creation_start = params.get("creation_start_date") or params.get("start_date")
    if creation_start:
        qs = qs.filter(created_at__date__gte=creation_start)
    
    creation_end = params.get("creation_end_date") or params.get("end_date")
    if creation_end:
        qs = qs.filter(created_at__date__lte=creation_end)

    # Date of Joining Filter
    doj_start = params.get("doj_start_date")
    if doj_start:
        qs = qs.filter(created_by__date_of_joining__gte=doj_start)
    
    doj_end = params.get("doj_end_date")
    if doj_end:
        qs = qs.filter(created_by__date_of_joining__lte=doj_end)

    return qs


def filter_legacy_leads(user, params, all_users=False):
    from lead.models import NewLead
    qs = NewLead.objects.all().order_by("-created_at") if all_users else NewLead.objects.filter(created_by=user).order_by("-created_at")

    # Search (General)
    search = params.get("search")
    if search:
        qs = qs.filter(
            Q(lead_id__icontains=search) |
            Q(phone__icontains=search) |
            Q(full_name__icontains=search)
        )

    # Specific Search/Filters
    lead_id = params.get("lead_code") or params.get("lead_id")
    if lead_id:
        qs = qs.filter(lead_id__iexact=lead_id)
        
    phone = params.get("contact_number") or params.get("phone")
    if phone:
        qs = qs.filter(phone__icontains=phone)
        
    full_name = params.get("customer_name") or params.get("full_name")
    if full_name:
        qs = qs.filter(full_name__icontains=full_name)

    # Product
    loan_type = params.get("product_subcategory") or params.get("loan_type")
    if loan_type:
        types = [t.strip() for t in loan_type.split(",") if t.strip()]
        if types:
            qs = qs.filter(loan_type__in=types)

    # Pincode, District, State
    pincode = params.get("pincode")
    if pincode:
        qs = qs.filter(pincode__icontains=pincode)
    
    district = params.get("district")
    if district:
        # NewLead has city, which might be used for district
        districts = [d.strip() for d in district.split(",") if d.strip()]
        dist_q = Q()
        for d in districts:
            dist_q |= Q(city__icontains=d)
        qs = qs.filter(dist_q)
    
    state = params.get("state")
    if state:
        states = [s.strip() for s in state.split(",") if s.strip()]
        state_q = Q()
        for s in states:
            state_q |= Q(state__icontains=s)
        qs = qs.filter(state_q)

    # Punched by (employee_id)
    punched_by = params.get("punched_by")
    if punched_by:
        qs = qs.filter(created_by__employee_id__iexact=punched_by)

    # Manager ID
    manager_id = params.get("manager_id")
    if manager_id:
        manager_id = str(manager_id).strip()
        manager_q = Q(created_by__assign_so__employee_id__iexact=manager_id)
        
        import uuid
        try:
            uuid.UUID(manager_id)
            manager_q |= Q(created_by__assign_so_id=manager_id)
        except ValueError:
            pass
            
        qs = qs.filter(manager_q)

    # Lending Partner
    lending_partner = params.get("lending_partner") or params.get("bank")
    if lending_partner:
        partners = [p.strip() for p in lending_partner.split(",") if p.strip()]
        if partners:
            from application.models import NewApplication
            new_apps_lead_ids = NewApplication.objects.filter(vendor__in=partners).values_list('account__lead_id', flat=True)
            qs = qs.filter(new_lead_id__in=new_apps_lead_ids)


    # Lead Type
    lead_type = params.get("lead_type")
    if lead_type:
        lead_types = [lt.strip() for lt in lead_type.split(",") if lt.strip()]
        if lead_types:
            qs = qs.filter(lead_type__in=[lt.upper() for lt in lead_types])

    # Source
    source = params.get("source")
    if source and source not in ["MoneyPal", "FINCOME"]:
        qs = qs.filter(source__iexact=source)

    # Status Mapping (Swati's comments)
    from utils.constants import NEW_LEAD_STATUS
    status = params.get("status")
    if status:
        status_list = [s.strip() for s in status.split(",") if s.strip()]
        mapped_statuses = []
        for s in status_list:
            if s.lower() == "active":
                mapped_statuses.append(NEW_LEAD_STATUS.NEW_LEAD.value)
            elif s.lower() == "auto close":
                mapped_statuses.append("AUTO_CLOSED")
            elif s.lower() == "application created":
                mapped_statuses.append(NEW_LEAD_STATUS.IN_PROGRESS.value)
            else:
                mapped_statuses.append(s)
        
        if mapped_statuses:
            qs = qs.filter(status__in=mapped_statuses)

    # Date Filter
    created_on = params.get("created_on")
    if created_on:
        qs = qs.filter(created_at__date=created_on)
    
    creation_start = params.get("creation_start_date") or params.get("start_date")
    if creation_start:
        qs = qs.filter(created_at__date__gte=creation_start)
    
    creation_end = params.get("creation_end_date") or params.get("end_date")
    if creation_end:
        qs = qs.filter(created_at__date__lte=creation_end)

    # Date of Joining Filter
    doj_start = params.get("doj_start_date")
    if doj_start:
        qs = qs.filter(created_by__date_of_joining__gte=doj_start)
    
    doj_end = params.get("doj_end_date")
    if doj_end:
        qs = qs.filter(created_by__date_of_joining__lte=doj_end)

    return qs


def prepare_application_create_data(user, data: dict, lead_obj: Optional[LeadV2]) -> dict:
    from utils.constants import ROLES
    payload = data.copy()
    product_category = getattr(lead_obj, "product_category", None) if lead_obj else payload.get("product_category")
    product_subcategory = getattr(lead_obj, "product_subcategory", None) if lead_obj else payload.get("product_subcategory")
    loan_type = payload.get("loan_type")

    payload["application_id"] = generate_application_id(product_category, product_subcategory, loan_type)
    payload["status"] = ApplicationStatus.DRAFT

    # Auto-populate punched_by and assigned_rh
    payload["punched_by"] = user.pk
    
    if user.role == ROLES.SALES_OFFICER.value:
        if user.assign_so and user.assign_so.role == ROLES.REGIONAL_HEAD.value:
            payload["assigned_rh"] = user.assign_so.pk

    if lead_obj:
        metadata = getattr(lead_obj, "metadata", {}) or {}
        lead_lending_partner = getattr(lead_obj, "lending_partner", None)
        metadata_lending_partner = metadata.get("lending_partner") if isinstance(metadata, dict) else None
        if not payload.get("lending_partner") and (lead_lending_partner or metadata_lending_partner):
            payload["lending_partner"] = lead_lending_partner or metadata_lending_partner
        if not payload.get("partner_branch_name") and getattr(lead_obj, "bank_branch", None):
            payload["partner_branch_name"] = lead_obj.bank_branch

    # Start each specialized journey at its first visible mobile stage.
    if loan_type == LeadType.BALANCE_TRANSFER:
        payload["stage"] = ApplicationStage.DOCUMENTS
        payload["pre_screen_completion"] = 0
        payload["post_screen_completion"] = resolve_post_screen_completion(ApplicationStage.DOCUMENTS)
    elif loan_type == LeadType.SELF_LENDING:
        payload["stage"] = ApplicationStage.LENDING_PARTNER_BANK
        payload["pre_screen_completion"] = 0
        payload["post_screen_completion"] = 0
    else:
        payload["stage"] = ApplicationStage.PAN
        payload["pre_screen_completion"] = resolve_pre_screen_completion(ApplicationStage.PAN)
        payload["post_screen_completion"] = 0
    return payload


def create_application(payload: dict) -> ApplicationV2:
    serializer = ApplicationCreateSerializer(data=payload)
    if not serializer.is_valid():
        raise ValueError(serializer.errors)

    try:
        with transaction.atomic():
            return serializer.save()
    except IntegrityError as exc:
        msg = str(exc)
        if "application_id" in msg:
            payload = payload.copy()
            # regenerate once and retry
            product_category = payload.get("product_category")
            product_subcategory = payload.get("product_subcategory")
            loan_type = payload.get("loan_type")
            payload["application_id"] = generate_application_id(product_category, product_subcategory, loan_type)
            serializer = ApplicationCreateSerializer(data=payload)
            if not serializer.is_valid():
                raise ValueError(serializer.errors)
            try:
                with transaction.atomic():
                    return serializer.save()
            except IntegrityError:
                raise ValueError("Application ID already exists. Please retry.")
        raise RuntimeError("Failed to create application")


def filter_applications(user, params):
    from users.models import User
    from utils.constants import ROLES

    if user.role in (ROLES.SUPER_ADMIN.value, ROLES.VERTICAL_ADMIN.value, ROLES.CPC.value):
        qs = ApplicationV2.objects.all()
    elif user.role == ROLES.SALES_OFFICER.value:
        agent_ids = list(User.objects.filter(assign_so=user).values_list('user_id', flat=True))
        agent_ids.append(user.user_id)
        qs = ApplicationV2.objects.filter(Q(lead__assigned_to_id__in=agent_ids) | Q(lead__created_by_id__in=agent_ids))
    elif user.role == ROLES.REGIONAL_HEAD.value:
        # RH can see applications of assigned SOs and their agents
        # 1. Direct reportees (SOs or Agents directly assigned to RH)
        direct_ids = list(User.objects.filter(assign_so=user).values_list('user_id', flat=True))
        # 2. Indirect reportees (Agents assigned to those SOs)
        indirect_ids = list(User.objects.filter(assign_so_id__in=direct_ids).values_list('user_id', flat=True))
        managed_user_ids = list(set(direct_ids + indirect_ids + [user.user_id]))
        qs = ApplicationV2.objects.filter(Q(lead__assigned_to_id__in=managed_user_ids) | Q(lead__created_by_id__in=managed_user_ids))
    elif user.role == ROLES.TELE_ADMIN.value:
        team_ids = [user.user_id]
        if getattr(user, 'team', None):
            team_ids = list(User.objects.filter(team=user.team).values_list('user_id', flat=True))
        qs = ApplicationV2.objects.filter(Q(lead__assigned_to_id__in=team_ids) | Q(lead__created_by_id__in=team_ids))
    else:
        qs = ApplicationV2.objects.filter(Q(lead__assigned_to=user) | Q(lead__created_by=user))

    qs = qs.order_by("-created_at")
    
    # Local Search
    search = params.get("search")
    if search:
        qs = qs.filter(
            Q(lead__customer_name__icontains=search) |
            Q(application_id__icontains=search) |
            Q(lead__contact_number__icontains=search) |
            Q(lead__customer_id__icontains=search)
        )

    # Specific Search/Filters
    application_id = params.get("application_id")
    if application_id:
        qs = qs.filter(application_id__icontains=application_id)
    
    customer_id = params.get("customer_id")
    if customer_id:
        qs = qs.filter(lead__customer_id__icontains=customer_id)

    lead_code = params.get("lead_code")
    if lead_code:
        qs = qs.filter(lead__lead_code__icontains=lead_code)
    
    contact_number = params.get("contact_number") or params.get("phone")
    if contact_number:
        qs = qs.filter(lead__contact_number__icontains=contact_number)
    
    customer_name = params.get("customer_name")
    if customer_name:
        qs = qs.filter(lead__customer_name__icontains=customer_name)

    # Punched by
    punched_by = params.get("punched_by") or params.get("punched by")
    if punched_by:
        qs = qs.filter(punched_by_id=punched_by)

    # Assigned RH
    assigned_rh = params.get("assigned_rh") or params.get("assigned_RH")
    if assigned_rh:
        qs = qs.filter(assigned_rh_id=assigned_rh)

    # Loan Type (Product Subcategory)
    loan_type = params.get("loan_type") or params.get("product_subcategory")
    if loan_type:
        subcats = [s.strip() for s in loan_type.split(",") if s.strip()]
        if subcats:
            qs = qs.filter(lead__product_subcategory__in=subcats)

    # Amount Range
    # Expected format: min_amount-max_amount (e.g., 0-200000, 200001-500000, 1000000+)
    amount_range = params.get("amount_range")
    if amount_range:
        if amount_range.endswith("+"):
            try:
                min_amt = float(amount_range[:-1])
                qs = qs.filter(lead__amount__gte=min_amt)
            except ValueError:
                pass
        elif "-" in amount_range:
            try:
                parts = amount_range.split("-")
                min_amt = float(parts[0])
                max_amt = float(parts[1])
                qs = qs.filter(lead__amount__gte=min_amt, lead__amount__lte=max_amt)
            except (ValueError, IndexError):
                pass

    # Date Range
    application_date = params.get("application_date") or params.get("date")
    if application_date:
        try:
            date_obj = datetime.strptime(application_date, "%Y-%m-%d").date()
            qs = qs.filter(created_at__date=date_obj)
        except ValueError:
            pass

    start_date = params.get("start_date")
    if start_date:
        try:
            qs = qs.filter(created_at__date__gte=datetime.strptime(start_date, "%Y-%m-%d").date())
        except ValueError:
            pass
    
    end_date = params.get("end_date")
    if end_date:
        try:
            qs = qs.filter(created_at__date__lte=datetime.strptime(end_date, "%Y-%m-%d").date())
        except ValueError:
            pass

    # Status
    status = params.get("status")
    if status:
        status_list = [s.strip() for s in status.split(",") if s.strip()]
        if status_list:
            qs = qs.filter(status__in=status_list)


    # Lead Type
    lead_type = params.get("lead_type")
    if lead_type:
        lead_types = [lt.strip() for lt in lead_type.split(",") if lt.strip()]
        if lead_types:
            qs = qs.filter(lead__lead_type__in=[lt.upper() for lt in lead_types])

    # Bank (Lending Partner)
    bank = params.get("bank") or params.get("lending_partner")
    if bank:
        banks = [b.strip() for b in bank.split(",") if b.strip()]
        if banks:
            qs = qs.filter(lending_partner__in=banks)

    # District
    district = params.get("district")
    if district:
        districts = [d.strip() for d in district.split(",") if d.strip()]
        if districts:
            pincode_qs = PincodeMaster.objects.filter(district__in=districts)
            matching_pincodes = pincode_qs.values_list('pincode', flat=True)
            qs = qs.filter(lead__pincode__in=matching_pincodes)

    return qs
