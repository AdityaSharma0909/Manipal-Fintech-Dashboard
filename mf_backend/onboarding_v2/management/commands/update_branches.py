import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from onboarding_v2.models import BankBranch


class Command(BaseCommand):
    help = (
        "Update existing BankBranch records: backfill district from city, "
        "and populate zone from a CSV/XLSX file."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            nargs="?",
            default=None,
            help="Path to the CSV/XLSX file containing zone data (optional). "
                 "Expected columns: branch_name or branch_code + zone.",
        )
        parser.add_argument(
            "--backfill-district",
            action="store_true",
            help="Copy city value into district for all branches where district is empty.",
        )
        parser.add_argument(
            "--overwrite-district",
            action="store_true",
            help="Overwrite district with city for ALL branches, even if district is already set.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without saving to the database.",
        )

    def handle(self, *args, **options):
        file_path = options.get("file_path")
        backfill_district = options["backfill_district"]
        overwrite_district = options["overwrite_district"]
        dry_run = options["dry_run"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE — no changes will be saved.\n"))

        district_updated = 0
        zone_updated = 0

        # ── Step 1: Backfill district from city ──────────────────────────
        if backfill_district or overwrite_district:
            self.stdout.write(self.style.NOTICE("Backfilling district from city..."))

            from django.db.models import Q

            if overwrite_district:
                # All branches that have a non-empty city
                branches = BankBranch.objects.exclude(
                    city__isnull=True
                ).exclude(city__exact="")
            else:
                # Only branches where district is blank/null but city exists
                branches = BankBranch.objects.filter(
                    Q(district__isnull=True) | Q(district__exact="")
                ).exclude(city__isnull=True).exclude(city__exact="")

            for branch in branches.iterator(chunk_size=500):
                if branch.city and branch.city.strip():
                    old_district = branch.district or ""
                    branch.district = branch.city.strip()
                    if not dry_run:
                        branch.save(update_fields=["district"])
                    district_updated += 1
                    if district_updated <= 10:  # show first few examples
                        self.stdout.write(
                            f"  {branch.branch_name}: district '{old_district}' → '{branch.district}'"
                        )

            self.stdout.write(
                self.style.SUCCESS(f"District updated for {district_updated} branches.")
            )

        # ── Step 2: Populate zone from CSV/XLSX ──────────────────────────
        if file_path:
            if not os.path.exists(file_path):
                raise CommandError(f"File not found: {file_path}")

            self.stdout.write(self.style.NOTICE(f"Reading zone data from {file_path}..."))

            try:
                ext = os.path.splitext(file_path)[1].lower()
                if ext == ".csv":
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)

                # Normalize column names
                df.columns = [
                    str(c).strip().lower().replace(" ", "_").replace(".", "")
                    for c in df.columns
                ]

                def clean_val(v):
                    if pd.isna(v) or v is None:
                        return ""
                    s = str(v).strip()
                    if s.lower() == "nan":
                        return ""
                    if s.endswith(".0"):
                        s = s[:-2]
                    return s

                matched = 0
                not_found = 0

                for _, row in df.iterrows():
                    zone = clean_val(row.get("zone"))
                    if not zone:
                        continue

                    # Try to match by branch_code first, then branch_name
                    branch_code = clean_val(
                        row.get("branch_code") or row.get("branch_id") or row.get("branchcode")
                    )
                    branch_name = clean_val(
                        row.get("branch_name") or row.get("branch") or row.get("branchname")
                    )

                    branch = None
                    if branch_code:
                        branch = BankBranch.objects.filter(branch_code=branch_code).first()
                    if not branch and branch_name:
                        branch = BankBranch.objects.filter(branch_name__iexact=branch_name).first()

                    if branch:
                        old_zone = branch.zone or ""
                        branch.zone = zone
                        if not dry_run:
                            branch.save(update_fields=["zone"])
                        zone_updated += 1
                        matched += 1
                        if zone_updated <= 10:
                            self.stdout.write(
                                f"  {branch.branch_name}: zone '{old_zone}' → '{zone}'"
                            )
                    else:
                        not_found += 1
                        if not_found <= 5:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  Branch not found: code='{branch_code}', name='{branch_name}'"
                                )
                            )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Zone update complete! Matched={matched}, Not Found={not_found}"
                    )
                )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error during zone update: {str(e)}"))
                import traceback
                traceback.print_exc()

        # ── Summary ──────────────────────────────────────────────────────
        if not backfill_district and not overwrite_district and not file_path:
            self.stdout.write(
                self.style.WARNING(
                    "Nothing to do! Use --backfill-district and/or provide a CSV file with zone data.\n"
                    "Examples:\n"
                    "  python manage.py update_branches --backfill-district\n"
                    "  python manage.py update_branches zones.csv\n"
                    "  python manage.py update_branches zones.csv --backfill-district\n"
                    "  python manage.py update_branches --backfill-district --dry-run\n"
                )
            )
        else:
            prefix = "[DRY RUN] " if dry_run else ""
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n{prefix}Summary: District updates={district_updated}, Zone updates={zone_updated}"
                )
            )

