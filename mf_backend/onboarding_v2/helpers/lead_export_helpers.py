import io
import pandas as pd
from datetime import datetime
from django.utils import timezone
from onboarding_v2.models import PincodeMaster
from onboarding_v2.serializers import LeadCreateSerializer
from users.models import User

from typing import Optional

def generate_leads_excel(qs) -> Optional[io.BytesIO]:
    v2_data = LeadCreateSerializer(qs, many=True).data

    def fmt_created(dt_val):
        try:
            if isinstance(dt_val, datetime):
                dt = dt_val
            elif isinstance(dt_val, str):
                s = dt_val.strip()
                if s.endswith("Z"):
                    s = s.replace("Z", "+00:00")
                dt = datetime.fromisoformat(s)
            else:
                return dt_val
            if timezone.is_naive(dt):
                dt = timezone.make_aware(dt, timezone.get_current_timezone())
            dt_local = timezone.localtime(dt)
            out = dt_local.strftime("%d %b, %Y, %I:%M %p")
            out = out.replace("AM", "am").replace("PM", "pm")
            return out
        except Exception:
            return dt_val

    def product_code(subcat):
        mapping = {
            "GOLD_LOAN": "GL",
            "PERSONAL_LOAN": "PL",
            "HOME_LOAN": "HL",
            "BUSINESS_LOAN": "BL",
            "LOAN_AGAINST_PROPERTY": "LAP",
            "WORKING_CAPITAL": "WC",
            "OVERDRAFT_DOD": "OD",
            "HEALTH_INSURANCE": "Insurance",
            "MOTOR_LOAN": "ML",
            "MOTOR_INSURANCE": "Insurance",
            "CREDIT_CARDS": "CC",
        }
        key = str(subcat or "").upper()
        return mapping.get(key, str(subcat or "UNKNOWN"))

    def product_display(item):
        code = product_code(item.get("product_subcategory"))
        lead_type = str(item.get("lead_type") or "").upper()
        if code == "GL" and lead_type:
            type_map = {
                "FRESH": "Fresh",
                "BALANCE_TRANSFER": "Balance Transfer",
                "CO_LENDING": "Co-Lending",
                "SELF_LENDING": "Self Lending",
            }
            suffix = type_map.get(lead_type, lead_type.title())
            return f"{code}-{suffix}"
        return code

    def with_location(item):
        pin = item.get("pincode")
        state = None
        district = None
        if pin:
            rec = PincodeMaster.objects.filter(pincode=pin).first()
            if rec:
                state = rec.statename
                district = rec.district
        item["state"] = state
        item["district"] = district
        return item

    v2_index = {str(l.id): l for l in qs}
    rows = []

    for item in v2_data:
        d = dict(item)
        d["product_display"] = product_display(d)
        d = with_location(d)
        lead_obj = v2_index.get(str(d.get("id")))
        punched_by = ""
        punched_team = ""
        if lead_obj and getattr(lead_obj, "created_by_id", None):
            try:
                user_obj = getattr(lead_obj, "created_by", None)
                if user_obj:
                    punched_by = str(getattr(user_obj, "employee_id", "") or "")
                    punched_team = str(getattr(user_obj, "team", "") or "")
                else:
                    u = User.objects.filter(user_id=lead_obj.created_by_id).only("employee_id", "team").first()
                    punched_by = str(getattr(u, "employee_id", "") or "")
                    punched_team = str(getattr(u, "team", "") or "")
            except Exception:
                punched_by = ""
                punched_team = ""
        created_display = None
        try:
            if lead_obj and getattr(lead_obj, "created_at", None):
                created_display = fmt_created(lead_obj.created_at)
        except Exception:
            created_display = fmt_created(d.get("created_at"))
        if not created_display:
            created_display = fmt_created(d.get("created_at"))

        rows.append({
            "Lead ID": d.get("lead_code"),
            "Customer Name": d.get("customer_name"),
            "Contact Number": d.get("contact_number"),
            "Product Category": d.get("product_category"),
            "Product Subcategory": d.get("product_subcategory"),
            "Product Display": d.get("product_display"),
            "Lead Type": d.get("lead_type"),
            "Amount": d.get("amount"),
            "Pincode": d.get("pincode"),
            "State": d.get("state"),
            "District": d.get("district"),
            "Punched By": punched_by,
            "Team": punched_team,
            "Manager ID": "",
            "Source": "Fincom" if getattr(lead_obj, "source", None) == "AGENT" else "MoneyPal",
            "Status": d.get("status"),
            "Created At": created_display,
        })

    columns = [
        "Lead ID",
        "Customer Name",
        "Contact Number",
        "Product Category",
        "Product Subcategory",
        "Product Display",
        "Lead Type",
        "Amount",
        "Pincode",
        "State",
        "District",
        "Punched By",
        "Team",
        "Manager ID",
        "Source",
        "Status",
        "Created At",
    ]

    if not rows:
        return None

    df_output = pd.DataFrame(rows, columns=columns)
    excel_file = io.BytesIO()
    xlwriter = pd.ExcelWriter(excel_file, engine='openpyxl')
    df_output.to_excel(xlwriter, 'Leads Report', index=False)
    xlwriter.close()
    excel_file.seek(0)
    return excel_file
