import os

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from onboarding_v2.models import BankBranch


class Command(BaseCommand):
    help = (
        "Import bank branch master data from CSV/XLSX. Supports columns like "
        "BranchName, SolId, Pincode, Dist_Name, State_Name, and BankName."
    )

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the CSV/XLSX file")
        parser.add_argument(
            "--sheet",
            type=str,
            default=None,
            help="Excel sheet name to read. Defaults to the first sheet.",
        )
        parser.add_argument(
            "--bank-name",
            type=str,
            default=None,
            help="Override bank name for every row. If omitted, BankName/bank_name from the file is used.",
        )
        parser.add_argument(
            "--replace-bank",
            action="store_true",
            help="Delete existing rows for the bank(s) in this file before importing.",
        )
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Delete all BankBranch rows before importing. Use carefully.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and preview import without saving changes.",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        sheet_name = options["sheet"]
        bank_name_override = options["bank_name"]
        replace_bank = options["replace_bank"]
        truncate = options["truncate"]
        dry_run = options["dry_run"]

        if replace_bank and truncate:
            raise CommandError("Use either --replace-bank or --truncate, not both.")
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        df = self._read_file(file_path, sheet_name)
        if df.empty:
            raise CommandError("The file is empty - nothing to import.")

        df.columns = [self._normalize_column(c) for c in df.columns]
        self.stdout.write(self.style.NOTICE(f"Rows found in file: {len(df)}"))
        self.stdout.write(self.style.NOTICE(f"Columns detected: {list(df.columns)}"))

        rows, skipped = self._build_rows(df, bank_name_override)
        if not rows:
            raise CommandError(f"No valid rows found. Skipped={skipped}")

        bank_names = sorted({row["bank_name"] for row in rows if row["bank_name"]})
        self.stdout.write(self.style.NOTICE(f"Banks in import: {bank_names}"))
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - no database changes will be saved."))

        created = 0
        updated = 0
        deleted = 0

        with transaction.atomic():
            if truncate:
                deleted = BankBranch.objects.count()
                if not dry_run:
                    BankBranch.objects.all().delete()
                self.stdout.write(self.style.WARNING(f"Truncate BankBranch rows: {deleted}"))

            if replace_bank and bank_names:
                qs = BankBranch.objects.filter(bank_name__in=bank_names)
                deleted = qs.count()
                if not dry_run:
                    qs.delete()
                self.stdout.write(
                    self.style.WARNING(f"Deleted existing rows for imported banks: {deleted}")
                )

            for row in rows:
                lookup = self._lookup_for_row(row)
                existing = BankBranch.objects.filter(**lookup).first() if lookup else None

                if existing:
                    for field, value in row.items():
                        setattr(existing, field, value)
                    if not dry_run:
                        existing.save(update_fields=list(row.keys()))
                    updated += 1
                else:
                    if not dry_run:
                        BankBranch.objects.create(**row)
                    created += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                "Import complete! "
                f"Created={created}, Updated={updated}, Skipped={skipped}, Deleted={deleted}"
            )
        )

    def _read_file(self, file_path, sheet_name):
        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext == ".csv":
                return pd.read_csv(file_path, dtype=str)
            if ext in (".xlsx", ".xls", ".xlsb", ".ods"):
                engine = "pyxlsb" if ext == ".xlsb" else ("odf" if ext == ".ods" else None)
                return pd.read_excel(file_path, sheet_name=sheet_name or 0, dtype=str, engine=engine)
        except Exception as exc:
            raise CommandError(f"Failed to read file: {exc}") from exc
        raise CommandError(f"Unsupported file format '{ext}'. Use .csv, .xlsx, .xls, .xlsb, or .ods.")

    def _build_rows(self, df, bank_name_override):
        rows = []
        skipped = 0

        for _, row in df.iterrows():
            branch_name = self._first(row, "branch_name", "branch", "branchname")
            bank_name = self._clean(bank_name_override) or self._first(row, "bank_name", "bankname", "bank")
            district = self._first(row, "district", "dist_name", "district_name")
            state = self._first(row, "state", "state_name")
            pincode = self._first(row, "pincode", "pin_code", "zip_code")

            if not all([bank_name, branch_name, district, state, pincode]):
                skipped += 1
                continue

            rows.append(
                {
                    "bank_name": bank_name,
                    "branch_name": branch_name,
                    "sol_id": self._first(row, "sol_id", "solid", "sol"),
                    "branch_code": self._first(row, "branch_code", "branchcode", "branch_id"),
                    "ifsc_code": self._first(row, "ifsc", "ifsc_code", "ifsc_number") or None,
                    "address": self._first(row, "address", "branch_address"),
                    "city": self._first(row, "city", "city_name", "dist_name"),
                    "district": district,
                    "correct_district": self._first(row, "correct_district"),
                    "state": state,
                    "pincode": pincode,
                    "glo_id": self._first(row, "glo_id", "gloid"),
                    "glo_name": self._first(row, "glo_name", "gloname"),
                    "agent_id": self._first(row, "agent_id", "agentid"),
                    "agent_name": self._first(row, "agent_name", "agentname"),
                    "agent_wise_status": self._first(row, "agent_wise_status"),
                    "zone": self._first(row, "zone"),
                }
            )

        return rows, skipped

    def _lookup_for_row(self, row):
        if row.get("bank_name") and row.get("sol_id"):
            return {"bank_name": row["bank_name"], "sol_id": row["sol_id"]}
        if row.get("bank_name") and row.get("ifsc_code"):
            return {"bank_name": row["bank_name"], "ifsc_code": row["ifsc_code"]}
        if row.get("bank_name") and row.get("branch_name") and row.get("pincode"):
            return {
                "bank_name": row["bank_name"],
                "branch_name": row["branch_name"],
                "pincode": row["pincode"],
            }
        return None

    def _normalize_column(self, value):
        return str(value).strip().lower().replace(" ", "_").replace(".", "")

    def _first(self, row, *keys):
        for key in keys:
            value = self._clean(row.get(key))
            if value:
                return value
        return ""

    def _clean(self, value):
        if pd.isna(value) or value is None:
            return ""
        cleaned = str(value).strip()
        if cleaned.lower() == "nan":
            return ""
        if cleaned.endswith(".0"):
            cleaned = cleaned[:-2]
        return cleaned
