import os

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from users.models import User
from utils.constants import TEAM


REQUIRED_COLUMNS = {
    "Emp ID",
    "In CRM (currently)",
    "To be changed to",
}


class Command(BaseCommand):
    help = "Update user teams from an Excel mapping file."

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the XLSX file")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Validate and preview changes without updating users.",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        dry_run = options["dry_run"]

        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        try:
            dataframe = pd.read_excel(
                file_path,
                dtype={"Emp ID": str},
            )
        except Exception as exc:
            raise CommandError(f"Failed to read Excel file: {exc}") from exc

        if dataframe.empty:
            raise CommandError("The file is empty - nothing to update.")

        dataframe.columns = dataframe.columns.str.strip()
        missing_columns = REQUIRED_COLUMNS.difference(dataframe.columns)
        if missing_columns:
            raise CommandError(
                "Missing required column(s): "
                + ", ".join(sorted(missing_columns))
            )

        employee_ids = dataframe["Emp ID"].map(self._clean_employee_id)
        duplicate_ids = sorted(
            employee_ids[
                employee_ids.notna() & employee_ids.duplicated(keep=False)
            ].unique()
        )
        if duplicate_ids:
            raise CommandError(
                "Duplicate employee ID(s) in the sheet: "
                + ", ".join(duplicate_ids)
            )

        valid_teams = {choice.value for choice in TEAM}
        stats = {
            "updated": 0,
            "already_correct": 0,
            "user_not_found": 0,
            "current_team_mismatch": 0,
            "invalid_row": 0,
        }

        self.stdout.write(self.style.NOTICE(f"Rows found: {len(dataframe)}"))
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN MODE - no database changes will be saved."
                )
            )

        with transaction.atomic():
            for index, row in dataframe.iterrows():
                excel_row = index + 2
                employee_id = self._clean_employee_id(row["Emp ID"])
                expected_team = self._normalize_team(
                    row["In CRM (currently)"]
                )
                target_team = self._normalize_team(
                    row["To be changed to"]
                )

                if (
                    not employee_id
                    or expected_team not in valid_teams
                    or target_team not in valid_teams
                ):
                    self.stdout.write(
                        self.style.ERROR(
                            f"[INVALID ROW] Excel row {excel_row}: "
                            f"employee_id={employee_id!r}, "
                            f"current={expected_team!r}, "
                            f"target={target_team!r}"
                        )
                    )
                    stats["invalid_row"] += 1
                    continue

                user = User.objects.filter(employee_id=employee_id).first()
                if user is None:
                    self.stdout.write(
                        self.style.ERROR(
                            f"[NOT FOUND] Excel row {excel_row}: "
                            f"Emp ID {employee_id}"
                        )
                    )
                    stats["user_not_found"] += 1
                    continue

                database_team = self._normalize_team(user.team)
                if database_team == target_team:
                    self.stdout.write(
                        f"[ALREADY CORRECT] Emp ID {employee_id}: "
                        f"team is already {target_team}"
                    )
                    stats["already_correct"] += 1
                    continue

                # Avoid overwriting a team changed after the sheet was prepared.
                if database_team != expected_team:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[CURRENT TEAM MISMATCH] Emp ID {employee_id}: "
                            f"sheet={expected_team}, "
                            f"database={database_team}"
                        )
                    )
                    stats["current_team_mismatch"] += 1
                    continue

                action = "WOULD UPDATE" if dry_run else "UPDATE"
                self.stdout.write(
                    f"[{action}] Emp ID {employee_id}: "
                    f"{database_team} -> {target_team}"
                )
                if not dry_run:
                    user.team = target_team
                    user.save(update_fields=["team"])
                stats["updated"] += 1

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(
            self.style.SUCCESS(
                "Team update complete! "
                f"Updated={stats['updated']}, "
                f"Already correct={stats['already_correct']}, "
                f"Not found={stats['user_not_found']}, "
                f"Current team mismatch={stats['current_team_mismatch']}, "
                f"Invalid rows={stats['invalid_row']}"
            )
        )

    @staticmethod
    def _clean_employee_id(value):
        if pd.isna(value):
            return None
        value = str(value).strip()
        if not value:
            return None
        if value.endswith(".0"):
            value = value[:-2]
        return value

    @staticmethod
    def _normalize_team(value):
        if pd.isna(value):
            return None
        value = str(value).strip().upper()
        return value or None
