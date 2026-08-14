import pandas as pd
from django.core.management.base import BaseCommand
from onboarding_v2.models import CustomerBankAccount

class Command(BaseCommand):
    help = "Updates existing CustomerBankAccount records with IFSC codes from an Excel file."

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the new Excel file containing IFSC codes",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview the changes without saving to the database.",
        )

    def handle(self, *args, **options):
        file_path = options["file_path"]
        dry_run = options["dry_run"]

        self.stdout.write(f"Reading file: {file_path}")
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to read file: {e}"))
            return

        if "Bank Name" not in df.columns or "First 4 IFSC Letters" not in df.columns:
            self.stdout.write(self.style.ERROR("Excel file must contain 'Bank Name' and 'First 4 IFSC Letters' columns."))
            return

        updated_count = 0
        skipped_count = 0

        for _, row in df.iterrows():
            bank_name = str(row.get("Bank Name", "")).strip()
            ifsc_prefix = str(row.get("First 4 IFSC Letters", "")).strip().upper()

            # Skip if prefix is invalid or not found
            if not ifsc_prefix or ifsc_prefix == "NAN" or len(ifsc_prefix) != 4:
                continue

            # Construct a valid IFSC code (11 characters: 4 letters + 0 + 6 alphanumeric)
            # Defaulting to 000001 for head office branch
            full_ifsc = f"{ifsc_prefix}0000000"

            # Find matching bank records in the database
            records = CustomerBankAccount.objects.filter(bank_name__iexact=bank_name)
            
            if records.exists():
                for record in records:
                    if record.ifsc_code != full_ifsc:
                        if not dry_run:
                            record.ifsc_code = full_ifsc
                            try:
                                record.save(update_fields=['ifsc_code'])
                                updated_count += 1
                                self.stdout.write(self.style.SUCCESS(f"Updated: {bank_name} -> {full_ifsc}"))
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"Error updating {bank_name}: {e}"))
                        else:
                            updated_count += 1
                            self.stdout.write(f"[DRY-RUN] Would update: {bank_name} -> {full_ifsc}")
                    else:
                        skipped_count += 1
            else:
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(f"\nCompleted! Updated: {updated_count}, Skipped/Unchanged/Not Found: {skipped_count}"))
