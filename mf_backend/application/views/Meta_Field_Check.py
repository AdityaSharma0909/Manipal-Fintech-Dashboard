from fuzzywuzzy import fuzz
from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from application.models import Application
from users.models import Address
from datetime import datetime, timedelta
from django.utils import timezone
import pytz


class MetaCheckerView(APIView):
    
    def get(self, request, *args, **kwargs):
        application_id = request.GET.get("application_id", "")
        application = Application.objects.get(application_id=application_id)
        account = application.account

        aadhaar_meta = getattr(account, "aadhar_meta_field", None)
        if aadhaar_meta:
            aadhaar_meta = {
                key.replace("aadhaar_", ""): value
                for key, value in aadhaar_meta.items()
            }
        pan_meta = getattr(account, "pan_meta_field", None)
        comparison_results = []

        if aadhaar_meta is not None:
            comparison_results.extend(self.compare_aadhaar_data(aadhaar_meta, account))

        if pan_meta is not None:
            comparison_results.extend(self.compare_pan_data(pan_meta, account))

        total_comparisons = len(comparison_results)
        matched_comparisons = sum(
            1 for comparison in comparison_results if comparison["matched"]
        )
        matching_percentage = (
            (matched_comparisons / total_comparisons) * 100
            if total_comparisons > 0
            else 0
        )

        matching_status = (
            "PASSED"
            if matching_percentage == 100
            else "WARNING" if 70 <= matching_percentage < 100 else "FAILED"
        )

        response_data = {
            "status": "success",
            "data": {
                "comparison_fields": comparison_results,
                "matching_percentage": round(matching_percentage, 2),
                "matching_status": matching_status,
            }
        }
        return HttpResponse.Success(response_data)

    def compare_aadhaar_data(self, aadhaar_meta, account):
        mapped_aadhaar_meta = {
            "dob": aadhaar_meta.get("dob", ""),
            "gender": aadhaar_meta.get("gender", ""),
            "full_name": aadhaar_meta.get("full_name", aadhaar_meta.get("name", "")),
            "care_of": aadhaar_meta.get("care_of", ""),
            "zip": aadhaar_meta.get("zip", aadhaar_meta.get("post_code", "")),
        }

        comparison_results = []

        def parse_date(date_str):
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            return None

        def add_comparison(input_value, meta_value, field_name):
            matched = fuzz.ratio(input_value.lower(), meta_value.lower()) > 95
            comparison_results.append(
                {
                    "field": f"Aadhaar {field_name.capitalize()}",
                    "input": input_value,
                    "actual_doc": meta_value,
                    "matched": matched,
                }
            )
            return matched

        if mapped_aadhaar_meta.get("dob") and account.year_of_birth:
            aadhaar_dob = parse_date(mapped_aadhaar_meta["dob"])
            if aadhaar_dob:
                account_year_of_birth = timezone.localtime(
                    account.year_of_birth, pytz.timezone("Asia/Kolkata")
                )
                add_comparison(
                    account_year_of_birth.strftime("%Y-%m-%d"),
                    aadhaar_dob.strftime("%Y-%m-%d"),
                    "dob",
                )

        if mapped_aadhaar_meta.get("gender") and account.gender:
            aadhaar_gender = (
                "Male" if mapped_aadhaar_meta["gender"] == "MALE" else "Female"
            )
            add_comparison(account.gender, aadhaar_gender, "gender")

        if mapped_aadhaar_meta.get("full_name") and account.user:
            full_name = f"{account.user.first_name} {account.user.last_name}"
            add_comparison(full_name, mapped_aadhaar_meta["full_name"], "full_name")

        if mapped_aadhaar_meta.get("care_of"):
            care_of = mapped_aadhaar_meta["care_of"]
            care_of_cleaned = (
                care_of.replace("S/O:", "")
                .replace("S/O","")
                .replace("W/O:", "")
                .replace("W/O","")
                .replace("Late", "")
                .strip()
            )

            if "W/O" in care_of and account.spouse_name:
                spouse_name_cleaned = account.spouse_name.replace("Late", "").strip()
                add_comparison(spouse_name_cleaned, care_of_cleaned, "care_of")
            elif account.father_name:
                father_name_cleaned = account.father_name.replace("Late", "").strip()
                add_comparison(father_name_cleaned, care_of_cleaned, "care_of")

        if mapped_aadhaar_meta.get("zip"):
            address = Address.objects.filter(
                account=account, pincode=mapped_aadhaar_meta["zip"]
            ).first()
            comparison_results.append(
                {
                    "field": "Aadhaar Pincode",
                    "input": address.pincode if address else None,
                    "actual_doc": mapped_aadhaar_meta["zip"],
                    "matched": bool(address),
                }
            )

        return comparison_results

    def compare_pan_data(self, pan_meta, account):
        mapped_pan_meta = {
            "first_name": pan_meta.get("firstName", pan_meta.get("first_name", "")),
            "last_name": pan_meta.get("lastName", pan_meta.get("last_name", "")),
            "id_holder_title": pan_meta.get(
                "idHolderTitle", pan_meta.get("pan_holder_title", "")
            ),
        }
        comparison_results = []

        def add_comparison(input_value, meta_value, field_name):
            matched = fuzz.ratio(input_value.lower(), meta_value.lower()) >= 95
            comparison_results.append(
                {
                    "field": f"PAN {field_name.capitalize()}",
                    "input": input_value,
                    "actual_doc": meta_value,
                    "matched": matched,
                }
            )
            return matched

        def get_pan_gender(title):
            if title == "Shri":
                return "Male"
            elif title in ["Smt", "Kumari"]:
                return "Female"
            else:
                return "Unknown"

        if mapped_pan_meta.get("first_name") and account.user:
            add_comparison(
                account.user.first_name, mapped_pan_meta["first_name"], "first_name"
            )

        if mapped_pan_meta.get("last_name") and account.user:
            add_comparison(
                account.user.last_name, mapped_pan_meta["last_name"], "last_name"
            )

        if mapped_pan_meta.get("id_holder_title") and account.gender:
            pan_gender = get_pan_gender(mapped_pan_meta["id_holder_title"])
            add_comparison(account.gender, pan_gender, "gender")

        return comparison_results