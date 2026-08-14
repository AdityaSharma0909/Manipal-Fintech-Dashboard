import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from onboarding_v2.models import BankBranch, PincodeMaster

class Command(BaseCommand):
    help = "Bulk import bank branches from a CSV/XLSX file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the CSV/XLSX file")
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Clear all existing bank branches before importing",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        truncate = options["truncate"]

        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        self.stdout.write(self.style.NOTICE(f"Starting import from {file_path}..."))

        try:
            # Read DataFrame based on file extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

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
                self.stdout.write(self.style.WARNING("Truncating BankBranch table..."))
                BankBranch.objects.all().delete()

            count = 0
            skipped = 0
            
            for _, row in df.iterrows():
                # Extract branch name
                branch_name = clean_val(row.get("branch_name") or row.get("branch") or row.get("branchname"))
                
                # Check for mandatory field (branch_name)
                if not branch_name:
                    skipped += 1
                    continue

                # Map branch id from Excel (or branch code) to branch_code field
                branch_code = clean_val(row.get("branch_id") or row.get("branch_code") or row.get("branchcode"))
                
                # Bank name is hardcoded to "Bajaj Finserv"
                bank_val = "Bajaj Finserv"

                # Map other fields from normalized columns
                address = clean_val(row.get("address") or row.get("branch_address"))
                city = clean_val(row.get("city") or row.get("city_name") or row.get("dist_name"))
                state = clean_val(row.get("state") or row.get("state_name"))
                pincode = clean_val(row.get("pincode") or row.get("pin_code") or row.get("zip_code"))
                zone = clean_val(row.get("zone"))

                district = ""
                if pincode:
                    pincode_obj = PincodeMaster.objects.filter(pincode=pincode).first()
                    if pincode_obj and pincode_obj.district:
                        district = pincode_obj.district.strip()
                if not district:
                    district = city

                defaults = {
                    "bank_name": bank_val,
                    "branch_name": branch_name,
                    "branch_code": branch_code,
                    "address": address,
                    "city": city,
                    "district": district,
                    "state": state,
                    "pincode": pincode,
                    "zone": zone,
                }

                # Create the branch record
                BankBranch.objects.create(**defaults)
                count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"Import complete! Result: Imported={count}, Skipped={skipped}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during import: {str(e)}"))
            import traceback
            traceback.print_exc()
