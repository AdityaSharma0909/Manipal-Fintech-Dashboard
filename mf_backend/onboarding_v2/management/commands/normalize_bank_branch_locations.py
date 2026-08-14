import re

from django.core.management.base import BaseCommand

from onboarding_v2.models import BankBranch


WORD_RE = re.compile(r"[A-Za-z]+")


def normalize_location_name(value):
    if value is None:
        return value

    value = str(value).strip()
    if not value:
        return value

    value = re.sub(r"\s+", " ", value.lower())
    return WORD_RE.sub(lambda match: match.group(0).capitalize(), value)


class Command(BaseCommand):
    help = (
        "Normalize BankBranch city, district, and state values to title case. "
        "Example: 'MADHYA PRADESH' becomes 'Madhya Pradesh'."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview changes without saving to the database.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Number of records to process per bulk update.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        batch_size = options["batch_size"]
        fields = ("city", "district", "state")
        pending_updates = []
        updated_count = 0
        scanned_count = 0
        examples = []

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - no changes will be saved.\n"))

        branches = BankBranch.objects.only("id", *fields).iterator(chunk_size=batch_size)

        for branch in branches:
            scanned_count += 1
            changes = {}

            for field in fields:
                old_value = getattr(branch, field)
                new_value = normalize_location_name(old_value)
                if new_value != old_value:
                    setattr(branch, field, new_value)
                    changes[field] = (old_value, new_value)

            if not changes:
                continue

            updated_count += 1
            if len(examples) < 10:
                examples.append((branch.id, changes))

            if not dry_run:
                pending_updates.append(branch)
                if len(pending_updates) >= batch_size:
                    BankBranch.objects.bulk_update(pending_updates, fields, batch_size=batch_size)
                    pending_updates = []

        if pending_updates:
            BankBranch.objects.bulk_update(pending_updates, fields, batch_size=batch_size)

        for branch_id, changes in examples:
            self.stdout.write(f"Branch {branch_id}:")
            for field, (old_value, new_value) in changes.items():
                self.stdout.write(f"  {field}: '{old_value}' -> '{new_value}'")

        prefix = "[DRY RUN] " if dry_run else ""
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{prefix}Completed. Scanned={scanned_count}, branches changed={updated_count}"
            )
        )
