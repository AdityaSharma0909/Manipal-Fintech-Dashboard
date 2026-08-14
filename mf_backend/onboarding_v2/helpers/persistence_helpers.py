from __future__ import annotations

import logging

from django.db import IntegrityError
from django.db.models import Q

from onboarding_v2.constants import AddressType, ApplicationStage, DocumentStatus, DocumentType, LeadType, LendingPartner
from onboarding_v2.models import (
    AdditionalDetailsV2,
    AddressV2,
    ApplicationDocument,
    ApplicationStageSnapshot,
    BankBranch,
    BankDetailsV2,
    JewelleryItem,
    LeadV2,
    Packet,
)
from onboarding_v2.saas import _resolve_jewellery_code_and_name
from onboarding_v2.services import generate_customer_id
from utils.helper import reverse_geocode_lat_lng


from decimal import Decimal

logger = logging.getLogger(__name__)


def update_application_processing_fee(application, amount=None):
    """
    Auto-calculate and save processing fee based on bureau score and Required Loan amount.
    If amount is provided, it is used for calculation; otherwise, it falls back to lead.amount.
    """
    from onboarding_v2.serializers import _pf_rate_for_score

    score = application.bureau_score
    # Use provided amount or fallback to lead.amount
    calc_amount = amount if amount is not None else application.lead.amount

    if calc_amount is None:
        logger.warning("Skipping PF calculation: Required Loan amount is missing | app=%s", application.application_id)
        return

    rate_percent = _pf_rate_for_score(score)
    pf_amount = (Decimal(str(calc_amount)) * rate_percent / Decimal("100")).quantize(Decimal("0.01"))

    if application.processing_fee != pf_amount:
        logger.info(
            "Updating processing fee | app=%s score=%s amount=%s rate=%s%% pf=%s",
            application.application_id,
            score,
            amount,
            rate_percent,
            pf_amount,
        )
        application.processing_fee = pf_amount
        application.save(update_fields=["processing_fee", "modified_at"])


def _get_stage_payload_dict(application) -> dict:
    """Helper to ensure stage_payload is returned as a dict."""
    if isinstance(application.stage_payload, dict):
        return application.stage_payload
    return {}


def persist_pan(application, payload):
    pan_number = payload.get("pan_number")
    file = payload.get("pan_image")
    name_on_pan = payload.get("name_on_pan")
    logger.info("Persisting PAN | app=%s pan=%s", application.application_id, pan_number)
    doc, _ = ApplicationDocument.objects.update_or_create(
        application=application,
        document_type=DocumentType.PAN,
        defaults={
            "status": DocumentStatus.VERIFIED,
            "metadata": {"pan_number": pan_number, "name_on_pan": name_on_pan},
        },
    )
    if file:
        doc.file = file
        doc.save()

    # Resolve customer_id according to PAN/phone dedupe rules
    lead = application.lead
    phone = lead.contact_number
    if name_on_pan and lead.customer_name != name_on_pan:
        lead.customer_name = name_on_pan
        lead.save(update_fields=["customer_name", "modified_at"])

    def _assign_customer_id(target_lead: LeadV2, cid: str):
        try:
            target_lead.customer_id = cid
            target_lead.save(update_fields=["customer_id", "modified_at"])
        except IntegrityError:
            raise ValueError("Customer already exists with this ID; please continue with the existing customer.")

    try:
        pan_owner_doc = (
            ApplicationDocument.objects.filter(
                document_type=DocumentType.PAN, metadata__pan_number=pan_number
            )
            .exclude(application=application)
            .select_related("application__lead")
            .first()
        )
    except Exception:
        pan_owner_doc = None
        for doc in ApplicationDocument.objects.filter(document_type=DocumentType.PAN).exclude(application=application):
            if (doc.metadata or {}).get("pan_number") == pan_number:
                pan_owner_doc = doc
                break
    pan_owner_lead = getattr(getattr(pan_owner_doc, "application", None), "lead", None)

    phone_owner_lead = (
        LeadV2.objects.filter(contact_number=phone, customer_id__isnull=False)
        .exclude(customer_id="")
        .exclude(id=lead.id)
        .first()
    )

    def _mask_phone(num: str) -> str:
        if not num:
            return ""
        return "+" + ("X" * max(len(num) - 4, 0)) + num[-4:]

    # Ensure existing PAN owner has a customer_id if missing
    if pan_owner_lead and not pan_owner_lead.customer_id:
        pan_owner_lead.customer_id = generate_customer_id()
        pan_owner_lead.save(update_fields=["customer_id", "modified_at"])

    if not pan_owner_lead and not phone_owner_lead:
        # New customer: generate fresh customer_id
        lead.customer_id = lead.customer_id or generate_customer_id()
        lead.save(update_fields=["customer_id", "modified_at"])
        return None

    if not pan_owner_lead and phone_owner_lead:
        # Phone already linked to another customer (different PAN): block
        raise ValueError(
            "Entered phone number is already linked with different pan. Please create a new lead with new phone number."
        )

    if pan_owner_lead and not phone_owner_lead:
        # Existing customer with new phone: reuse customer_id from PAN owner
        _assign_customer_id(lead, pan_owner_lead.customer_id)
        # Update old customer's phone to the new one (scenario 3 requirement)
        if phone and phone != pan_owner_lead.contact_number:
            try:
                pan_owner_lead.contact_number = phone
                pan_owner_lead.save(update_fields=["contact_number", "modified_at"])
            except IntegrityError:
                # Some environments may still have a uniqueness constraint on contact_number.
                # Do not fail PAN stage completion when this best-effort sync conflicts.
                logger.warning(
                    "Skipped PAN owner phone sync due to integrity conflict | app=%s pan_owner=%s phone=%s",
                    application.application_id,
                    pan_owner_lead.id,
                    phone,
                )
        masked = _mask_phone(pan_owner_lead.contact_number)
        return {
            "message": f"We already have the details of Customer: {pan_owner_lead.customer_name} ({pan_owner_lead.customer_id})",
            "detail": f"You are continuing Onboarding of Customer ID: {pan_owner_lead.customer_id} with linked phone {masked}",
        }

    if pan_owner_lead and phone_owner_lead:
        if pan_owner_lead.customer_id == phone_owner_lead.customer_id:
            # Repeat customer with linked mobile number: reuse
            _assign_customer_id(lead, pan_owner_lead.customer_id)
            masked = _mask_phone(phone_owner_lead.contact_number)
            return {
                "message": f"We already have the details of Customer: {pan_owner_lead.customer_name} ({pan_owner_lead.customer_id})",
                "detail": f"You are continuing Onboarding of Customer ID: {pan_owner_lead.customer_id} with linked phone {masked}",
            }
        # Phone linked to different PAN: block
        masked_linked = _mask_phone(phone_owner_lead.contact_number)
        raise ValueError(
            f"Entered phone number is already linked with different pan. Please create a new lead with new phone number or use linked phone number '{masked_linked}'"
        )

    return None


def persist_loan_range_selection(application, payload):
    loan_amount = payload.get("loan_amount")
    if loan_amount:
        application.lead.amount = loan_amount
        application.lead.save(update_fields=["amount", "modified_at"])
    application.stage_payload = {**_get_stage_payload_dict(application), "loan_range_selection": payload}
    application.save(update_fields=["stage_payload", "modified_at"])


def persist_product_selection(application, payload):
    application.stage_payload = {**_get_stage_payload_dict(application), "product_selection": payload}
    application.save(update_fields=["stage_payload", "modified_at"])


def _partner_bank_names(lending_partner):
    if not lending_partner:
        return []

    names = {str(lending_partner).strip()}
    for value, label in LendingPartner.choices:
        if lending_partner == value or lending_partner == label:
            names.add(value)
            names.add(label)
    return [name for name in names if name]


def _filter_branch_qs(filters, lending_partner):
    logger.info("Filtering BankBranch queryset | filters=%s lending_partner=%s", filters, lending_partner)
    qs = BankBranch.objects.filter(**filters).exclude(sol_id__isnull=True).exclude(sol_id="")
    bank_names = _partner_bank_names(lending_partner)
    if not bank_names:
        return qs

    bank_query = Q()
    for bank_name in bank_names:
        bank_query |= Q(bank_name__iexact=bank_name)
    return qs.filter(bank_query)


def _resolve_branch_sol_id(lending_partner, branch_name):
    filters = {}
    if branch_name:
        filters["branch_name__iexact"] = str(branch_name).strip()   

    if not filters:
        return None

    branch = _filter_branch_qs(filters, lending_partner).first()
    if branch:
        return str(branch.sol_id).strip()

    # fallback_filters = {}
    # if branch_code:
    #     fallback_filters["branch_code__iexact"] = str(branch_code).strip()
    # elif branch_name:
    #     fallback_filters["branch_name__iexact"] = str(branch_name).strip()

    # if not fallback_filters:
    #     return None

    # branch = _filter_branch_qs(fallback_filters, lending_partner).first()
    # return str(branch.sol_id).strip() if branch else None


def persist_lending_partner_bank(application, payload):
    lending_partner = payload.get("lending_partner")
    partner_branch_code = payload.get("lending_partner_branch_code")
    partner_branch_name = payload.get("lending_partner_branch_name")
    pincode = payload.get("pincode")
    logger.info(
        "Persisting lending partner bank | app=%s partner=%s branch_code=%s branch_name=%s pincode=%s",
        application.application_id,
        lending_partner,
        partner_branch_code,
        partner_branch_name,
        pincode,
    )
    sol_id = _resolve_branch_sol_id(lending_partner, partner_branch_name)
    logger.info(
        "Resolved branch sol_id |sol_id=%s",
        sol_id,
    )   
    client_loan_id = f"GLN{sol_id}7" if sol_id else None

    if lending_partner:
        application.lending_partner = lending_partner
    if "lending_partner_branch_code" in payload:
        application.partner_branch_code = partner_branch_code
    if partner_branch_name:
        application.partner_branch_name = partner_branch_name
    application.client_loan_id = client_loan_id
    if client_loan_id:
        payload["client_loan_id"] = client_loan_id
    application.save(update_fields=["lending_partner", "partner_branch_code", "partner_branch_name", "client_loan_id", "modified_at"])

    lead = application.lead
    if lending_partner and lead.lending_partner != lending_partner:
        lead.lending_partner = lending_partner
        lead.save(update_fields=["lending_partner", "modified_at"])

    application.stage_payload = {**_get_stage_payload_dict(application), "lending_partner_bank": payload}
    application.save(update_fields=["stage_payload", "modified_at"])
    return payload


def persist_basic(application, payload):
    loan_type = payload.get("loan_type")
    if loan_type:
        application.loan_type = loan_type
        application.save(update_fields=["loan_type", "modified_at"])
        lead = application.lead
        if lead.lead_type != loan_type:
            lead.lead_type = loan_type
            lead.save(update_fields=["lead_type", "modified_at"])


def annotate_poa_ids(payload):
    if not isinstance(payload, dict):
        return
    poa = payload.get("poa", [])
    for i, doc_payload in enumerate(poa):
        doc_payload["id"] = str(i + 1)


def annotate_pledge_ids(payload):
    if not isinstance(payload, dict):
        return
    pledge_cards = payload.get("pledge_cards", [])
    for i, card in enumerate(pledge_cards):
        if not isinstance(card, dict):
            continue
        card["id"] = str(i + 1)
        images = card.get("images", [])
        if isinstance(images, list):
            new_images = []
            for j, img in enumerate(images):
                if isinstance(img, str):
                    new_images.append({"file_url": img, "id": str(j + 1)})
                elif isinstance(img, dict):
                    img["id"] = str(j + 1)
                    new_images.append(img)
            card["images"] = new_images


def annotate_customer_visit_ids(payload):
    if not isinstance(payload, dict):
        return
    image_fields = [
        "customer_visit_image_url",
        "house_exterior_image_url",
        "house_interior_image_url",
        "door_number_image_url",
        "street_view_1_image_url",
        "street_view_2_image_url",
    ]
    for i, field in enumerate(image_fields):
        val = payload.get(field)
        if not val:
            continue
        
        meta = {"id": str(i + 1), "status": DocumentStatus.UPLOADED}
        # Only customer_visit_image_url gets GPS and timestamp metadata
        if field == "customer_visit_image_url":
            val_dict = val if isinstance(val, dict) else {}
            lat = payload.get("latitude") or val_dict.get("latitude")
            lon = payload.get("longitude") or val_dict.get("longitude")
            loc = payload.get("location") or val_dict.get("location")
            ts = payload.get("timestamp") or val_dict.get("timestamp")

            if lat and lon:
                geocoded = reverse_geocode_lat_lng(lat, lon, default_location=loc)
                if geocoded:
                    loc = geocoded
                    payload["location"] = geocoded
                    if isinstance(val, dict):
                        val["location"] = geocoded

            if lat:
                meta["latitude"] = str(lat)
            if lon:
                meta["longitude"] = str(lon)
            if ts:
                meta["timestamp"] = str(ts)
            if loc:
                meta["location"] = loc

        if isinstance(val, str) and val.strip():
            payload[field] = {"file_url": val, **meta}
        elif isinstance(val, dict) and val.get("file_url"):
            val.update({k: v for k, v in meta.items() if not val.get(k)})


def persist_addresses(application, payload, secondary=False):
    # secondary=True indicates address_secondary stage
    annotate_poa_ids(payload)
    if secondary:
        address_data = payload.get("current") or {}
        address_type = AddressType.CURRENT
        logger.info("Persisting secondary address | app=%s", application.application_id)
        _upsert_address(application, address_type, address_data)
        return

    permanent = payload.get("permanent") or {}
    current_same = payload.get("current_same_as_permanent")
    current = permanent if current_same else payload.get("current") or {}
    mailing = payload.get("mailing") or {}
    _upsert_address(application, AddressType.PERMANENT, permanent)
    _upsert_address(application, AddressType.CURRENT, current)
    if mailing:
        _upsert_address(application, AddressType.MAILING, mailing)

    # Handle POA documents
    poa = payload.get("poa", [])
    for i, doc_payload in enumerate(poa):
        doc_id = doc_payload.get("id")
        doc_type = doc_payload.get("document_type")
        subtype = doc_payload.get("subtype")
        existing = ApplicationDocument.objects.filter(
            application=application,
            document_type=doc_type,
            metadata__id=doc_id
        ).first()
        if existing:
            existing.status = doc_payload.get("status", DocumentStatus.UPLOADED)
            new_metadata = {**existing.metadata, **doc_payload.get("metadata", {}), "id": doc_id}
            existing.metadata = new_metadata
            if doc_payload.get("file"):
                existing.file = doc_payload["file"]
            if doc_payload.get("file_url"):
                existing.file_url = doc_payload["file_url"]
            existing.save()
        else:
            ApplicationDocument.objects.create(
                application=application,
                document_type=doc_type,
                subtype=subtype,
                status=doc_payload.get("status", DocumentStatus.UPLOADED),
                metadata={**doc_payload.get("metadata", {}), "id": doc_id},
                file=doc_payload.get("file"),
                file_url=doc_payload.get("file_url"),
            )


def _upsert_address(application, address_type, data):
    AddressV2.objects.update_or_create(
        application=application,
        address_type=address_type,
        defaults={
            "address_line1": data.get("address_line1"),
            "address_line2": data.get("address_line2"),
            "address_line3": data.get("address_line3"),
            "pincode": data.get("pincode"),
            "state": data.get("state"),
            "district": data.get("district"),
            "city": data.get("city"),
            "metadata": {},
        },
    )


def persist_documents(application, payload):
    docs = payload if isinstance(payload, list) else []
    for doc_payload in docs:
        doc_type = doc_payload.get("document_type")
        subtype = doc_payload.get("subtype")
        status = doc_payload.get("status", DocumentStatus.UPLOADED)
        metadata = doc_payload.get("metadata", {})
        file_obj = doc_payload.get("file")
        file_url = doc_payload.get("file_url")

        # Try to find an existing doc with the same file_url, or same type/subtype if we're updating
        qs = ApplicationDocument.objects.filter(
            application=application,
            document_type=doc_type,
        )
        if file_url:
            existing = qs.filter(file_url=file_url).first()
        else:
            # If no file_url, use the most recent one with same type/subtype
            existing = qs.filter(subtype=subtype).order_by("-modified_at", "-created_at").first()
        
        if existing:
            existing.status = status
            existing.metadata = metadata
            if file_obj:
                existing.file = file_obj
            if file_url:
                existing.file_url = file_url
            existing.save()
            continue

        ApplicationDocument.objects.create(
            application=application,
            document_type=doc_type,
            subtype=subtype,
            status=status,
            metadata=metadata,
            file=file_obj if file_obj else None,
            file_url=file_url if file_url else None,
        )


def persist_personal(application, payload):
    # Store on application.stage_payload for now (could be normalized later)
    application.stage_payload = {**_get_stage_payload_dict(application), "personal": payload}
    updates = {
        "primary_borrower_type": payload.get("primary_borrower_type") or application.primary_borrower_type,
        "nationality": payload.get("nationality") or application.nationality,
        "nri_status": payload.get("nri_status") or application.nri_status,
        "caste": payload.get("caste") or application.caste,
        "occupation": payload.get("occupation") or application.occupation,
        "income_source": payload.get("income_source") or application.income_source,
    }
    update_fields = ["stage_payload", "modified_at"]
    for field, value in updates.items():
        if value is not None and value != "":
            setattr(application, field, value)
            update_fields.append(field)
    if len(update_fields) > 2:
        logger.info(
            "Persisting personal | app=%s fields=%s",
            application.application_id,
            [f for f in update_fields if f not in ("stage_payload", "modified_at")],
        )
    application.save(update_fields=update_fields)


def persist_gold(application, payload):
    code_counts = {}
    packet = Packet.objects.filter(application=application).order_by("id").first()
    if not packet:
        packet = Packet(application=application)

    packet_updates = {
        "packet_id": payload.get("packet_id"),
        "barcode_id": payload.get("barcode_id"),
        "gross_weight": payload.get("gross_weight"),
        "gross_value": payload.get("gross_value"),
        "net_adjusted_weight": payload.get("net_adjusted_weight"),
        "net_adjusted_value": payload.get("net_adjusted_value"),
        "appraiser_id": payload.get("appraiser_id"),
        "appraiser_name": payload.get("appraiser_name"),
    }
    for field, value in packet_updates.items():
        if value is not None and value != "":
            setattr(packet, field, value)
    packet.save()
    Packet.objects.filter(application=application).exclude(pk=packet.pk).delete()
    # Clear and recreate items for simplicity
    packet.items.all().delete()
    for item in payload.get("items", []):
        code, _ = _resolve_jewellery_code_and_name(item.get("type_of_jewellery"))
        code_counts[code] = code_counts.get(code, 0) + 1

        meta = {}
        # Support URL-based uploads (bypass app server) if provided
        if item.get("front_image_url"):
            meta["front_image_url"] = item.get("front_image_url")
        if item.get("back_image_url"):
            meta["back_image_url"] = item.get("back_image_url")
        if item.get("weighing_machine_image_url"):
            meta["weighing_machine_image_url"] = item.get("weighing_machine_image_url")
        if item.get("appraiser_certificate_image_url"):
            meta["appraiser_certificate_image_url"] = item.get("appraiser_certificate_image_url")

        JewelleryItem.objects.create(
            packet=packet,
            type_of_jewellery=item.get("type_of_jewellery"),
            number_of_articles=item.get("number_of_articles"),
            purity=item.get("purity"),
            gross_weight=item.get("gross_weight"),
            stone_weight=item.get("stone_weight"),
            net_weight=item.get("net_weight"),
            impurity_deducted=item.get("impurity_deducted"),
            net_adjusted_weight=item.get("net_adjusted_weight"),
            percent_of_gold=item.get("percent_of_gold"),
            actual_gold_rate=item.get("actual_gold_rate"),
            gross_value=item.get("gross_value"),
            net_value=item.get("net_value"),
            net_adjusted_value=item.get("net_adjusted_value"),
            front_image_url=item.get("front_image_url"),
            back_image_url=item.get("back_image_url"),
            weighing_machine_image_url=item.get("weighing_machine_image_url"),
            appraiser_certificate_image_url=item.get("appraiser_certificate_image_url"),
            metadata=meta,
        )


def persist_loan(application, payload):
    # Persist loan_type/subcategory to application and propagate to lead if changed
    loan_type = payload.get("loan_type")
    loan_subcategory = payload.get("loan_subcategory")
    update_fields = []
    if loan_type:
        application.loan_type = loan_type
        update_fields.append("loan_type")
    if update_fields:
        update_fields.append("modified_at")
        application.save(update_fields=update_fields)

    # Required Loan amount (requested_amount or required_bt_amount) from payload
    required_amount = payload.get("requested_amount") or payload.get("required_bt_amount")

    updates = {}
    mapping = {
        "partner_branch_code": "partner_branch_code",
        "partner_branch_name": "partner_branch_name",
        "partner_product_code": "partner_product_code",
        "agreement_id": "agreement_id",
        "spread_id": "spread_id",
        "ltr": "ltr",
        "interest_start_date": "interest_start_date",
        "loan_maturity_date": "loan_maturity_date",
        "first_repayment_date": "first_repayment_date",
        "stamp_duty": "stamp_duty",
        "insurance_charges": "insurance_charges",
        "documentation_charges": "documentation_charges",
        "other_charges": "other_charges",
        "total_charges": "total_charges",
        "consent_timestamp": "consent_timestamp",
        "consent_ip": "consent_ip",
        "reference_number": "reference_number",
        "compliance": "compliance",
        "source_id": "source_id",
        "multi_appraisal": "multi_appraisal",
        "number_of_animal_cattle": "number_of_animal_cattle",
    }
    for payload_key, field_name in mapping.items():
        if payload_key in payload:
            updates[field_name] = payload.get(payload_key)
    if updates:
        for field, value in updates.items():
            setattr(application, field, value)
        update_fields = list(updates.keys())
        update_fields.append("modified_at")
        application.save(update_fields=update_fields)
        logger.info("Persisting loan meta | app=%s fields=%s", application.application_id, list(updates.keys()))

    # Auto-calculate processing fee using the amount from the LOAN stage payload
    update_application_processing_fee(application, amount=required_amount)


def persist_self_declaration(application, payload):
    updates = {
        "consent_timestamp": payload.get("consent_timestamp"),
        "consent_ip": payload.get("consent_ip"),
    }
    update_fields = []
    for field, value in updates.items():
        if value is not None:
            setattr(application, field, value)
            update_fields.append(field)
    if update_fields:
        application.save(update_fields=[*update_fields, "modified_at"])


def persist_charges(application, payload):
    charge_fields = (
        "processing_fee",
        "stamp_duty",
        "insurance_charges",
        "documentation_charges",
        "other_charges",
        "total_charges",
    )
    update_fields = []
    for field in charge_fields:
        if field in payload:
            setattr(application, field, payload.get(field))
            update_fields.append(field)
    if update_fields:
        application.save(update_fields=[*update_fields, "modified_at"])


def persist_bank(application, payload):
    cheque_url = payload.get("cheque_image_url")
    metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    if not cheque_url and metadata:
        cheque_url = metadata.get("cheque_image_url")
    if not cheque_url:
        try:
            snap = application.stage_snapshots.get(stage=ApplicationStage.BANK)
            snap_payload = snap.payload if isinstance(snap.payload, dict) else {}
            if isinstance(snap_payload.get("metadata"), dict):
                cheque_url = snap_payload.get("metadata", {}).get("cheque_image_url")
        except ApplicationStageSnapshot.DoesNotExist:
            pass
    BankDetailsV2.objects.update_or_create(
        application=application,
        defaults={
            "cheque_image_url": cheque_url,
            "bank_name": payload.get("bank_name"),
            "account_number": payload.get("account_number"),
            "customer_name_as_per_bank": payload.get("customer_name_as_per_bank"),
            "ifsc_code": payload.get("ifsc_code"),
            "branch_name": payload.get("branch_name"),
            "metadata": {**metadata, **({"cheque_image_url": cheque_url} if cheque_url else {})},
        },
    )


def _persist_bt_additional(application, payload):
    """Persist BT additional details into stage_payload."""
    additional_data = {
        "rental_income": payload.get("rental_income"),
        "annual_income_family_range": payload.get("annual_income_family_range"),
        "house_ownership": payload.get("house_ownership"),
        "due_diligence_checklist": payload.get("due_diligence_checklist") or [],
        "reference_1": payload.get("reference_1") or {},
        "reference_2": payload.get("reference_2") or {},
    }
    application.stage_payload = {**_get_stage_payload_dict(application), "additional": additional_data}
    application.save(update_fields=["stage_payload", "modified_at"])


def persist_additional(application, payload):
    if application.loan_type == LeadType.BALANCE_TRANSFER:
        _persist_bt_additional(application, payload)
        return

    metadata = {
        "rental_income": payload.get("rental_income"),
        "annual_income_family_range": payload.get("annual_income_family_range"),
        "house_ownership": payload.get("house_ownership"),
        "due_diligence_checklist": payload.get("due_diligence_checklist") or [],
        "reference_1": payload.get("reference_1") or {},
        "reference_2": payload.get("reference_2") or {},
    }

    AdditionalDetailsV2.objects.update_or_create(
        application=application,
        defaults={
            "is_employee": payload.get("is_employee", False),
            "nominee_relation": payload.get("nominee_relation"),
            "nominee_full_name": payload.get("nominee_full_name"),
            "nominee_contact_number": payload.get("nominee_contact_number"),
            "metadata": metadata,
        },
    )


def persist_customer_visit(application, payload):
    """
    Persist BT customer visit images and GPS coordinates.
    Images are stored as ApplicationDocument records plus a summary in stage_payload.
    """
    cvi = payload.get("customer_visit_image_url")
    cvi_dict = cvi if isinstance(cvi, dict) else {}

    latitude = payload.get("latitude") or cvi_dict.get("latitude")
    longitude = payload.get("longitude") or cvi_dict.get("longitude")
    location = payload.get("location") or cvi_dict.get("location")
    timestamp = payload.get("timestamp") or cvi_dict.get("timestamp")

    if latitude and longitude:
        geocoded = reverse_geocode_lat_lng(latitude, longitude, default_location=location)
        if geocoded:
            location = geocoded
            payload["location"] = geocoded
            if isinstance(cvi, dict):
                cvi["location"] = geocoded

    image_fields = {
        "CUSTOMER_VISIT_IMG": payload.get("customer_visit_image_url"),
        "HOUSE_EXTERIOR_IMG": payload.get("house_exterior_image_url"),
        "HOUSE_INTERIOR_IMG": payload.get("house_interior_image_url"),
        "DOOR_NUMBER_IMG": payload.get("door_number_image_url"),
        "STREET_VIEW_1_IMG": payload.get("street_view_1_image_url"),
        "STREET_VIEW_2_IMG": payload.get("street_view_2_image_url"),
    }
    for subtype, img_obj in image_fields.items():
        if not img_obj:
            continue
        
        url = img_obj.get("file_url") if isinstance(img_obj, dict) else img_obj
        if not url:
            continue
            
        doc_meta = img_obj.copy() if isinstance(img_obj, dict) else {}
        if subtype == "CUSTOMER_VISIT_IMG":
            if latitude:
                doc_meta["latitude"] = str(latitude)
            if longitude:
                doc_meta["longitude"] = str(longitude)
            if location:
                doc_meta["location"] = location

        ApplicationDocument.objects.update_or_create(
            application=application,
            document_type=DocumentType.CUSTOMER_VISIT,
            subtype=subtype,
            defaults={
                "file_url": url,
                "status": doc_meta.get("status", DocumentStatus.UPLOADED),
                "metadata": doc_meta,
            },
        )

    visit_data = {
        "customer_visit_image_url": payload.get("customer_visit_image_url"),
        "house_exterior_image_url": payload.get("house_exterior_image_url"),
        "house_interior_image_url": payload.get("house_interior_image_url"),
        "door_number_image_url": payload.get("door_number_image_url"),
        "street_view_1_image_url": payload.get("street_view_1_image_url"),
        "street_view_2_image_url": payload.get("street_view_2_image_url"),
        "latitude": str(latitude or ""),
        "longitude": str(longitude or ""),
        "timestamp": str(timestamp or ""),
        "location": location,
        "metadata": payload.get("metadata") or {},
    }
    application.stage_payload = {**_get_stage_payload_dict(application), "customer_visit": visit_data}
    application.save(update_fields=["stage_payload", "modified_at"])


def persist_selfie(application, payload):
    """
    Persist Selfie image and GPS coordinates.
    """
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    location = payload.get("location")

    if latitude and longitude:
        geocoded = reverse_geocode_lat_lng(latitude, longitude, default_location=location)
        if geocoded:
            location = geocoded
            payload["location"] = geocoded

    file_obj = payload.get("file")
    file_url = payload.get("file_url")
    
    doc, _ = ApplicationDocument.objects.update_or_create(
        application=application,
        document_type=DocumentType.SELFIE,
        defaults={
            "status": DocumentStatus.UPLOADED,
            "metadata": {
                "latitude": str(latitude or ""),
                "longitude": str(longitude or ""),
                "timestamp": str(payload.get("timestamp", "")),
                "location": location,
            },
        },
    )
    if file_obj:
        doc.file = file_obj
        doc.save()
    if file_url:
        doc.file_url = file_url
        doc.save()

    selfie_data = {
        "file_url": doc.file_url,
        "latitude": str(latitude or ""),
        "longitude": str(longitude or ""),
        "timestamp": str(payload.get("timestamp", "")),
        "location": location,
        "metadata": payload.get("metadata") or {},
    }
    application.stage_payload = {**_get_stage_payload_dict(application), "selfie": selfie_data}
    application.save(update_fields=["stage_payload", "modified_at"])


def persist_pledge_card(application, payload):
    """
    Persist BT pledge card details to stage_payload.
    """
    pledge_cards = payload.get("pledge_cards", [])
    pledge_data = {
        "pledge_cards": pledge_cards,
        "total_pledge_value": sum(
            float(card.get("loan_amount", 0)) 
            for card in pledge_cards if isinstance(card, dict)
        ),
    }
    application.stage_payload = {**_get_stage_payload_dict(application), "pledge_card": pledge_data}
    application.save(update_fields=["stage_payload", "modified_at"])


def persist_eligibility(application, payload):
    """
    Persist BT eligibility details into stage_payload and update application fields.
    """
    eligibility_data = {
        "credit_bureau_url": payload.get("credit_bureau_url"),
        "score_band": payload.get("score_band"),
        "score_color": payload.get("score_color"),
        "score_value": payload.get("score_value"),
        "metadata": payload.get("metadata") or {},
    }
    application.stage_payload = {**_get_stage_payload_dict(application), "eligibility": eligibility_data}
    
    # Update canonical fields on application if provided
    if payload.get("score_value") is not None:
        application.bureau_score = payload.get("score_value")
    if payload.get("score_color") is not None:
        application.score_color = payload.get("score_color")
    
    application.save(update_fields=["stage_payload", "bureau_score", "score_color", "modified_at"])


def persist_waiver(application, payload):
    """
    Persist BT waiver details. Computes processing fee, waiver amount, and final fee.
    Saves to stage_payload and updates application.processing_fee.
    """
    from decimal import Decimal
    from onboarding_v2.serializers import _pf_rate_for_score

    bureau_score = application.bureau_score
    loan_amount = Decimal(str(application.lead.amount or 0))
    pf_rate = _pf_rate_for_score(bureau_score)
    processing_fee = (loan_amount * pf_rate / Decimal("100")).quantize(Decimal("0.01"))

    waiver_opted = payload.get("waiver_opted", False)
    waiver_pct = Decimal(str(payload.get("waiver_percentage") or 0))
    waiver_amount = Decimal("0")
    final_fee = processing_fee

    if waiver_opted and waiver_pct > 0:
        waiver_amount = (processing_fee * waiver_pct / Decimal("100")).quantize(Decimal("0.01"))
        final_fee = (processing_fee - waiver_amount).quantize(Decimal("0.01"))

    waiver_data = {
        "processing_fee": str(processing_fee),
        "waiver_opted": waiver_opted,
        "waiver_percentage": str(waiver_pct) if waiver_opted else None,
        "waiver_amount": str(waiver_amount),
        "final_processing_fee": str(final_fee),
        "remarks": payload.get("remarks"),
        "proof_1_url": payload.get("proof_1_url"),
        "proof_2_url": payload.get("proof_2_url"),
        "metadata": payload.get("metadata") or {},
    }
    application.processing_fee = final_fee
    application.stage_payload = {**_get_stage_payload_dict(application), "waiver": waiver_data}
    application.save(update_fields=["processing_fee", "stage_payload", "modified_at"])


def normalize_bt_waiver_payload(payload):
    """Remove stale waiver details when a BT customer opts out."""
    if isinstance(payload, dict) and payload.get("waiver_opted") is False:
        return {"waiver_opted": False}
    return payload


def persist_amount_transferred(application, payload):
    """
    Persist BT amount transferred details and update application status.
    """
    from onboarding_v2.constants import ApplicationStatus

    status_map = {
        "Yes": ApplicationStatus.AMOUNT_PAID_TO_EXISTING_LENDER,
        "No": ApplicationStatus.AMOUNT_NOT_PAID_TO_EXISTING_LENDER,
        "On-Hold": ApplicationStatus.AMOUNT_PAID_TO_EXISTING_LENDER_ON_HOLD,
    }
    
    transfer_status = payload.get("amount_transferred_status")
    app_status = status_map.get(transfer_status)
    
    if app_status:
        application.status = app_status
    
    transfer_data = {
        "amount_transferred_status": transfer_status,
        "reason": payload.get("reason"),
        "remarks": payload.get("remarks"),
        "metadata": payload.get("metadata") or {},
    }
    application.stage_payload = {**_get_stage_payload_dict(application), "amount_transferred": transfer_data}
    application.save(update_fields=["status", "stage_payload", "modified_at"])


def persist_gold_received(application, payload):
    """
    Persist BT gold received details and update application status.
    """
    from onboarding_v2.constants import ApplicationStatus

    status_map = {
        "Yes": ApplicationStatus.GOLD_RECEIVED_FROM_EXISTING_LENDER,
        "No": ApplicationStatus.GOLD_NOT_RECEIVED_FROM_EXISTING_LENDER,
        "On-Hold": ApplicationStatus.GOLD_RECEIVED_FROM_EXISTING_LENDER_ON_HOLD,
    }
    
    gold_status = payload.get("gold_received_status")
    app_status = status_map.get(gold_status)
    
    if app_status:
        application.status = app_status
    
    gold_data = {
        "gold_received_status": gold_status,
        "reason": payload.get("reason"),
        "remarks": payload.get("remarks"),
        "metadata": payload.get("metadata") or {},
    }
    application.stage_payload = {**_get_stage_payload_dict(application), "gold_received": gold_data}
    application.save(update_fields=["status", "stage_payload", "modified_at"])


def persist_gold_submitted(application, payload):
    """
    Persist BT gold submitted details and update application status.
    """
    from onboarding_v2.constants import ApplicationStatus

    status_map = {
        "Yes": ApplicationStatus.GOLD_SUBMITTED_TO_PARTNER_BANK,
        "No": ApplicationStatus.GOLD_NOT_SUBMITTED_TO_PARTNER_BANK,
        "On-Hold": ApplicationStatus.GOLD_SUBMITTED_TO_PARTNER_BANK_ON_HOLD,
    }
    
    gold_status = payload.get("gold_submitted_status")
    app_status = status_map.get(gold_status)
    
    if app_status:
        application.status = app_status
    
    gold_data = {
        "gold_submitted_status": gold_status,
        "reason": payload.get("reason"),
        "remarks": payload.get("remarks"),
        "metadata": payload.get("metadata") or {},
    }
    application.stage_payload = {**_get_stage_payload_dict(application), "gold_submitted": gold_data}
    application.save(update_fields=["status", "stage_payload", "modified_at"])


def persist_choose_customer(application, payload):
    """
    Persist BT customer choice and update application status.
    """
    from onboarding_v2.constants import ApplicationStatus

    choice = payload.get("customer_choice")
    relationship = payload.get("relationship")
    if choice == "Self":
        application.status = ApplicationStatus.NEW_LOAN_TAKEN_BY_SELF
    elif choice == "Others":
        application.status = ApplicationStatus.LOAN_TRANSFERRED
    
    customer_data = {
        "customer_choice": choice,
        "relationship": relationship,
        "customer_name": application.lead.customer_name if choice == "Self" else None,
        "metadata": payload.get("metadata") or {},
    }
    application.stage_payload = {**_get_stage_payload_dict(application), "choose_customer": customer_data}
    application.save(update_fields=["status", "stage_payload", "modified_at"])


def persist_fund_refund(application, payload):
    """
    Persist BT fund refund details as an array into stage_payload.
    """
    from onboarding_v2.constants import TransactionStatus, ApplicationStage
    from onboarding_v2.helpers.fund_refund_helpers import update_bt_return_completed_status
    from django.utils import timezone
    
    previous_status = application.status
    current_payload = _get_stage_payload_dict(application)
    refunds = current_payload.get("fund_refund", [])
    if not isinstance(refunds, list):
        refunds = []
    
    # If no refunds in stage_payload, check the stage snapshot
    if not refunds:
        try:
            snapshot = application.stage_snapshots.get(stage=ApplicationStage.FUND_REFUND)
            if isinstance(snapshot.payload, list):
                refunds = snapshot.payload
        except Exception:
            pass

    # Determine cheque_image_urls (always a list)
    cheque_image_urls = payload.get("cheque_image_urls")
    if cheque_image_urls is None:
        cheque_image_url = payload.get("cheque_image_url")
        if isinstance(cheque_image_url, list):
            cheque_image_urls = cheque_image_url
        elif cheque_image_url:
            cheque_image_urls = [cheque_image_url]
        else:
            cheque_image_urls = []
    
    new_refund = {
        "id": str(len(refunds) + 1),
        "amount": str(payload.get("amount")),
        "payment_mode": payload.get("payment_mode"),
        "bank_name": payload.get("bank_name"),
        "transaction_reference_number": payload.get("transaction_reference_number"),
        "fund_transferred_by": payload.get("fund_transferred_by"),
        "cheque_image_urls": cheque_image_urls,
        "transaction_proof_url": payload.get("transaction_proof_url"),
        "relationship": payload.get("relationship"),
        "relationship_proof_url": payload.get("relationship_proof_url"),
        "status": TransactionStatus.UNVERIFIED,
        "created_at": timezone.now().isoformat(),
        "metadata": payload.get("metadata") or {},
    }
    
    # If it's a BT application, send to SAAS synchronously before saving
    if application.loan_type == LeadType.BALANCE_TRANSFER:
        from onboarding_v2.helpers.saas_helpers import call_fund_refund_sync
        call_fund_refund_sync(application, new_refund)
    
    refunds.append(new_refund)
    application.stage_payload = {**current_payload, "fund_refund": refunds}
    application.save(update_fields=["stage_payload", "modified_at"])
    update_bt_return_completed_status(application, previous_status)

    return refunds
