import pandas as pd

from onboarding_v2.models import PincodeMaster, BankBranch


def _read_df(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    return pd.read_excel(uploaded_file)


def import_pincodes(uploaded_file, truncate=False):
    df = _read_df(uploaded_file)
    df.columns = [c.strip().lower() for c in df.columns]

    if truncate:
        PincodeMaster.objects.all().delete()

    count = 0
    for _, row in df.iterrows():
        pincode = str(row.get("pincode") or "").strip()
        if not pincode:
            continue
        defaults = {
            "district": row.get("district"),
            "statename": row.get("statename"),
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude"),
            "circlename": row.get("circlename"),
            "regionname": row.get("regionname"),
            "divisionname": row.get("divisionname"),
        }
        PincodeMaster.objects.update_or_create(pincode=pincode, defaults=defaults)
        count += 1
    return count


def import_bank_branches(uploaded_file, truncate=False, lender_code=None, bank_name=None):
    df = _read_df(uploaded_file)
    # Strip whitespace and normalize column names
    df.columns = [str(c).strip().lower().replace(" ", "_").replace(".", "") for c in df.columns]

    def clean_val(v):
        if pd.isna(v) or v is None:
            return ""
        s = str(v).strip()
        if s.lower() == "nan":
            return ""
        if s.endswith(".0"):
            s = s[:-2]
        return s

    if truncate:
        BankBranch.objects.all().delete()

    count = 0
    skipped = 0
    for _, row in df.iterrows():
        # Enhanced mapping for common column names
        sol_id = clean_val(row.get("sol_id") or row.get("solid") or row.get("sol"))
        glo_id = clean_val(row.get("glo_id") or row.get("gloid"))
        ifsc = clean_val(row.get("ifsc") or row.get("ifsc_code") or row.get("ifsc_number"))
        
        # Mandatory field extraction with aliases
        branch_name = clean_val(row.get("branch_name") or row.get("branch") or row.get("branchname"))
        bank_val = clean_val(bank_name or row.get("bank_name") or row.get("bankname") or "Axis Bank")
        city = clean_val(row.get("city") or row.get("city_name") or row.get("dist_name"))
        state = clean_val(row.get("state") or row.get("state_name"))
        district = clean_val(row.get("district") or row.get("dist_name") or row.get("district_name"))
        pincode = clean_val(row.get("pincode") or row.get("pin_code") or row.get("zip_code"))

        # Skip if mandatory fields are missing (sol_id, city are optional)
        if not all([bank_val, branch_name, state, district, pincode]):
            skipped += 1
            continue

        defaults = {
            "bank_name": bank_val,
            "branch_name": branch_name,
            "glo_id": glo_id,
            "glo_name": clean_val(row.get("glo_name") or row.get("gloname")),
            "agent_id": clean_val(row.get("agent_id") or row.get("agentid")),
            "agent_name": clean_val(row.get("agent_name") or row.get("agentname")),
            "agent_wise_status": clean_val(row.get("agent_wise_status")),
            "district": district,
            "correct_district": clean_val(row.get("correct_district")),
            "sol_id": sol_id,
            "ifsc_code": ifsc or None,
            "branch_code": clean_val(row.get("branch_code") or row.get("branchcode")),
            "address": clean_val(row.get("address")),
            "city": city,
            "state": state,
            "pincode": pincode,
        }

        BankBranch.objects.create(**defaults)
        count += 1
    return {"imported": count, "skipped": skipped}
