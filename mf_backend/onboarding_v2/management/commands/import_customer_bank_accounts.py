import os
import re

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

from onboarding_v2.models import CustomerBankAccount

IFSC_REGEX = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")

# Possible column name variations (case-insensitive matching)
COLUMN_MAP = {
    "bank_name": ["bank_name", "bank name", "bankname", "name"],
    "ifsc_code": ["ifsc_code", "ifsc code", "ifsccode", "ifsc"],
    "branch": ["branch", "branch_name", "branch name", "branchname"],
}


def _match_column(df_columns, aliases):
    """Return the first matching column name from the dataframe (case-insensitive)."""
    lower_map = {col.strip().lower(): col for col in df_columns}
    for alias in aliases:
        if alias.lower() in lower_map:
            return lower_map[alias.lower()]
    return None


class Command(BaseCommand):
    help = "Bulk import Customer Bank Accounts from a CSV, Excel (.xlsx), or ODS file"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the CSV, Excel (.xlsx), or ODS file",
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
            "--skip-errors",
            action="store_true",
            help="Skip rows with validation errors instead of aborting.",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        sheet_name = options["sheet"]
        dry_run = options["dry_run"]
        skip_errors = options["skip_errors"]

        # ------------------------------------------------------------------
        # 1. Read the file
        # ------------------------------------------------------------------
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        try:
            if ext in (".xlsx", ".xls", ".ods"):
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet_name or 0,
                    dtype=str,
                    engine="odf" if ext == ".ods" else None
                )
            elif ext == ".csv":
                df = pd.read_csv(file_path, dtype=str)
            else:
                raise CommandError(
                    f"Unsupported file format '{ext}'. Use .xlsx, .xls, .csv, or .ods"
                )
        except Exception as e:
            raise CommandError(f"Failed to read file: {e}")

        if df.empty:
            raise CommandError("The file is empty - nothing to import.")

        # ------------------------------------------------------------------
        # 2. Map columns
        # ------------------------------------------------------------------
        col_bank = _match_column(df.columns, COLUMN_MAP["bank_name"])
        col_ifsc = _match_column(df.columns, COLUMN_MAP["ifsc_code"])
        col_branch = _match_column(df.columns, COLUMN_MAP["branch"])

        missing = []
        if not col_bank:
            missing.append("bank_name")

        if missing:
            raise CommandError(
                f"Could not find required column(s): {', '.join(missing)}. "
                f"Available columns: {list(df.columns)}"
            )

        self.stdout.write(
            self.style.NOTICE(
                f"Detected columns -> bank_name='{col_bank}', "
                f"ifsc_code='{col_ifsc}', branch='{col_branch}'"
            )
        )
        self.stdout.write(
            self.style.NOTICE(f"Total rows in file: {len(df)}")
        )

        # ------------------------------------------------------------------
        # 3. Validate & import
        # ------------------------------------------------------------------
        created = 0
        skipped_duplicate = 0
        skipped_error = 0
        errors = []

        for idx, row in df.iterrows():
            row_num = idx + 2  # Excel row (1-indexed header + data)

            bank_name = str(row[col_bank]).strip() if col_bank and pd.notna(row[col_bank]) else ""
            ifsc_code = str(row[col_ifsc]).strip().upper() if col_ifsc and pd.notna(row[col_ifsc]) else "XXXX0000000"
            if len(ifsc_code) >= 4:
                ifsc_code = ifsc_code[:4] + "0000000"
            branch = str(row[col_branch]).strip() if col_branch and pd.notna(row[col_branch]) else "DEFAULT BRANCH"

            # --- Validation ---
            row_errors = []
            if not bank_name:
                row_errors.append("bank_name is empty")
            if not ifsc_code:
                row_errors.append("ifsc_code is empty")
            elif not IFSC_REGEX.match(ifsc_code):
                row_errors.append(f"invalid IFSC format: '{ifsc_code}'")
            if not branch:
                row_errors.append("branch is empty")

            if row_errors:
                msg = f"Row {row_num}: {'; '.join(row_errors)}"
                if skip_errors:
                    self.stdout.write(self.style.WARNING(f"  SKIP  {msg}"))
                    skipped_error += 1
                    continue
                else:
                    errors.append(msg)
                    continue

            # --- Insert ---
            if dry_run:
                self.stdout.write(
                    f"  [DRY-RUN] Row {row_num}: "
                    f"{bank_name} | {ifsc_code} | {branch}"
                )
                created += 1
                continue

            try:
                _, was_created = CustomerBankAccount.objects.get_or_create(
                    bank_name=bank_name,
                    ifsc_code=ifsc_code,
                    defaults={"branch": branch},
                )
                if was_created:
                    created += 1
                else:
                    skipped_duplicate += 1
            except IntegrityError:
                skipped_duplicate += 1
            except Exception as e:
                msg = f"Row {row_num}: {e}"
                if skip_errors:
                    self.stdout.write(self.style.WARNING(f"  SKIP  {msg}"))
                    skipped_error += 1
                else:
                    errors.append(msg)

        # ------------------------------------------------------------------
        # 4. Report
        # ------------------------------------------------------------------
        if errors and not skip_errors:
            self.stdout.write(self.style.ERROR("\nValidation errors found:"))
            for err in errors:
                self.stdout.write(self.style.ERROR(f"  - {err}"))
            raise CommandError(
                f"Import aborted due to {len(errors)} error(s). "
                "Fix the file or re-run with --skip-errors."
            )

        prefix = "[DRY-RUN] " if dry_run else ""
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix}Import complete!\n"
                f"  Created:           {created}\n"
                f"  Skipped (duplicate):{skipped_duplicate}\n"
                f"  Skipped (errors):  {skipped_error}\n"
                f"  Total rows:        {len(df)}"
            )
        )
