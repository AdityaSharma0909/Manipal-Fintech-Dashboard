import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, IntegrityError

from onboarding_v2.models import Customers

class Command(BaseCommand):
    help = "Bulk import Customers from a CSV, Excel (.xlsx, .xls, .xlsb), or ODS file"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the CSV, Excel (.xlsx, .xls, .xlsb), or ODS file",
        )
        parser.add_argument(
            "--sheet",
            type=str,
            default=None,
            help="Sheet name to read (Excel only). Defaults to the first sheet.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and preview data without saving to the database.",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Clear all existing customer records before importing.",
        )
        parser.add_argument(
            "--skip-errors",
            action="store_true",
            help="Skip rows with validation errors instead of aborting.",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        sheet_name = options["sheet"]
        dry_run = options["dry_run"]
        truncate = options["truncate"]
        skip_errors = options["skip_errors"]

        # ------------------------------------------------------------------
        # 1. Read the file
        # ------------------------------------------------------------------
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext in (".xlsx", ".xls", ".ods", ".xlsb"):
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet_name or 0,
                    dtype=str,
                    engine="pyxlsb" if ext == ".xlsb" else ("odf" if ext == ".ods" else None)
                )
            elif ext == ".csv":
                df = pd.read_csv(file_path, dtype=str)
            else:
                raise CommandError(
                    f"Unsupported file format '{ext}'. Use .xlsx, .xls, .xlsb, .csv, or .ods"
                )
        except Exception as e:
            raise CommandError(f"Failed to read file: {e}")

        if df.empty:
            raise CommandError("The file is empty - nothing to import.")

        # ------------------------------------------------------------------
        # 2. Map columns
        # ------------------------------------------------------------------
        col_map = {}
        name_columns = []
        for col in df.columns:
            col_lower = str(col).strip().lower()
            # 1. Match Customer ID
            if "customer" in col_lower and "id" in col_lower:
                col_map["customer_id"] = col
            elif "customerid" in col_lower or "cust_id" in col_lower or col_lower in ("id", "custid"):
                if "customer_id" not in col_map:
                    col_map["customer_id"] = col
            elif "flid" in col_lower or col_lower in ("fl id", "fl_id"):
                col_map["fl_id"] = col
            
            # 2. Match Phone Number
            elif "phone" in col_lower or "contact" in col_lower or "mobile" in col_lower:
                col_map["phone_number"] = col
            
            # 3. Match PAN Number
            elif "pan" in col_lower:
                col_map["pan_number"] = col
            
            # 4. Match Name
            elif "name" in col_lower:
                name_columns.append(col)
                if "name" not in col_map:
                    col_map["name"] = col
            
            # 5. Match Defaulter checkbox
            elif "defaulter" in col_lower:
                col_map["is_defaulter"] = col

        # Fallbacks for exact or normalized match if not matched by substring
        for col in df.columns:
            col_norm = str(col).strip().lower().replace(" ", "").replace("_", "").replace("-", "")
            if "customer_id" not in col_map and col_norm in ["customerid", "custid", "id"]:
                col_map["customer_id"] = col
            if "fl_id" not in col_map and col_norm in ["flid"]:
                col_map["fl_id"] = col
            if "phone_number" not in col_map and col_norm in ["phone", "phonenumber", "contact", "contactnumber", "mobile", "mobilenumber"]:
                col_map["phone_number"] = col
            if "pan_number" not in col_map and col_norm in ["pan", "pannumber", "pancard"]:
                col_map["pan_number"] = col
            if "name" not in col_map and col_norm in ["name", "customername", "fullname"]:
                col_map["name"] = col
            if "is_defaulter" not in col_map and col_norm in ["defaulter", "isdefaulter", "defaultercheckbox"]:
                col_map["is_defaulter"] = col

        if "customer_id" not in col_map and "fl_id" not in col_map:
            raise CommandError(
                f"Could not find required column for Customer ID or FL ID. "
                f"Available columns: {list(df.columns)}"
            )

        self.stdout.write(self.style.NOTICE(f"Detected mapping:"))
        for target, mapped in col_map.items():
            self.stdout.write(self.style.NOTICE(f"  {target} -> '{mapped}'"))
        self.stdout.write(self.style.NOTICE(f"Total rows in file: {len(df)}"))

        # Helper clean functions
        def clean_str(val):
            if pd.isna(val) or val is None:
                return ""
            s = str(val).strip()
            if s.lower() == "nan":
                return ""
            if s.endswith(".0"):
                s = s[:-2]
            return s

        def clean_bool(val):
            if pd.isna(val) or val is None:
                return False
            s = str(val).strip().lower()
            if s in ["true", "1", "yes", "y", "t", "defaulter", "checked"]:
                return True
            return False

        def first_clean_value(row, columns):
            for column in columns:
                value = clean_str(row.get(column))
                if value:
                    return value
            return ""

        # ------------------------------------------------------------------
        # 3. Validate & import
        # ------------------------------------------------------------------
        created = 0
        updated = 0
        skipped_error = 0
        errors = []

        try:
            with transaction.atomic():
                if truncate and not dry_run:
                    self.stdout.write(self.style.WARNING("Clearing existing customers table..."))
                    Customers.objects.all().delete()

                for idx, row in df.iterrows():
                    row_num = idx + 2  # Excel row numbering (header at row 1)

                    cust_id = clean_str(row.get(col_map["customer_id"])) if "customer_id" in col_map else ""
                    fl_id = clean_str(row.get(col_map["fl_id"])) if "fl_id" in col_map else ""
                    cust_name = first_clean_value(row, name_columns)
                    phone = clean_str(row.get(col_map["phone_number"])) if "phone_number" in col_map else ""
                    pan = clean_str(row.get(col_map["pan_number"])) if "pan_number" in col_map else ""
                    is_defaulter = clean_bool(row.get(col_map["is_defaulter"])) if "is_defaulter" in col_map else True

                    if not cust_id and not fl_id:
                        msg = f"Row {row_num}: Customer ID/FL ID is empty."
                        if skip_errors:
                            self.stdout.write(self.style.WARNING(f"  SKIP  {msg}"))
                            skipped_error += 1
                            continue
                        else:
                            errors.append(msg)
                            continue

                    if dry_run:
                        self.stdout.write(
                            f"  [DRY-RUN] Row {row_num}: "
                            f"CustomerID={cust_id or '-'} | FLID={fl_id or '-'} | "
                            f"{cust_name} | {phone} | {pan} | Defaulter={is_defaulter}"
                        )
                        created += 1
                        continue

                    try:
                        defaults = {
                            "customer_id": cust_id or None,
                            "fl_id": fl_id or None,
                            "name": cust_name,
                            "phone_number": phone,
                            "pan_number": pan,
                            "is_defaulter": is_defaulter,
                        }
                        lookup = {"customer_id": cust_id} if cust_id else {"fl_id": fl_id}
                        obj, was_created = Customers.objects.update_or_create(**lookup, defaults=defaults)
                        if was_created:
                            created += 1
                        else:
                            updated += 1
                    except Exception as e:
                        msg = f"Row {row_num}: {e}"
                        if skip_errors:
                            self.stdout.write(self.style.WARNING(f"  SKIP  {msg}"))
                            skipped_error += 1
                        else:
                            errors.append(msg)

        except Exception as e:
            raise CommandError(f"Database transaction error: {e}")

        # ------------------------------------------------------------------
        # 4. Report
        # ------------------------------------------------------------------
        if errors and not skip_errors:
            self.stdout.write(self.style.ERROR("\nValidation errors found during processing:"))
            for err in errors:
                self.stdout.write(self.style.ERROR(f"  - {err}"))
            raise CommandError(
                f"Import aborted due to {len(errors)} error(s). "
                "Fix the file or run with --skip-errors."
            )

        prefix = "[DRY-RUN] " if dry_run else ""
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix}Import complete!\n"
                f"  Created:           {created}\n"
                f"  Updated:           {updated}\n"
                f"  Skipped (errors):  {skipped_error}\n"
                f"  Total rows:        {len(df)}"
            )
        )
