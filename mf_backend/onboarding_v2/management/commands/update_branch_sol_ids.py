import sys
from django.core.management.base import BaseCommand
from onboarding_v2.models import BankBranch

class Command(BaseCommand):
    help = (
        "Updates BankBranch sol_id values to be at least 3 digits: "
        "if 2 digits, prefixes with one zero; if 1 digit, prefixes with two zeros; "
        "if no digits (None or empty string), updates to three zeros."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview the changes without saving them to the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE — no changes will be saved to the database.\n"))

        branches = BankBranch.objects.all()
        total_count = branches.count()
        updated_count = 0
        skipped_count = 0

        self.stdout.write(f"Processing {total_count} bank branches...")

        for branch in branches.iterator(chunk_size=1000):
            old_sol_id = branch.sol_id
            
            # Stripped sol_id or empty string
            val = str(old_sol_id or "").strip()
            
            # Determine new sol_id based on user requirements
            if len(val) == 0:
                new_sol_id = "000"
            elif len(val) == 1:
                new_sol_id = f"00{val}"
            elif len(val) == 2:
                new_sol_id = f"0{val}"
            else:
                new_sol_id = val

            if old_sol_id != new_sol_id:
                if not dry_run:
                    branch.sol_id = new_sol_id
                    branch.save(update_fields=["sol_id"])
                
                updated_count += 1
                # Log first 20 changes or every 100th change
                if updated_count <= 20 or updated_count % 100 == 0:
                    action_prefix = "[DRY-RUN] Would update" if dry_run else "Updated"
                    self.stdout.write(
                        f"  {action_prefix}: '{branch.bank_name} - {branch.branch_name}' (ID: {branch.id}): "
                        f"sol_id '{old_sol_id}' -> '{new_sol_id}'"
                    )
            else:
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nFinished! Total processed: {total_count}. "
                f"Updated: {updated_count}. Skipped/Unchanged: {skipped_count}."
            )
        )
