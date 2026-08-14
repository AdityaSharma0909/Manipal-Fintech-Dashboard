import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from onboarding_v2.models import PincodeMaster


class Command(BaseCommand):
    help = "Bulk import pincodes from a CSV/XLSX file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the CSV/XLSX file")
        parser.add_argument(
            "--truncate",
            action="store_true",
            help="Clear all existing pincodes before importing",
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
                self.stdout.write(self.style.WARNING("Truncating PincodeMaster table..."))
                PincodeMaster.objects.all().delete()

            count = 0
            skipped = 0

            if truncate:
                # Fast path using bulk_create
                objs = []
                for _, row in df.iterrows():
                    pincode_raw = clean_val(row.get("pincode"))
                    if not pincode_raw:
                        skipped += 1
                        continue

                    # Pad with zero if numeric to make it 6 digits
                    if pincode_raw.isdigit():
                        pincode = f"{int(pincode_raw):06d}"
                    else:
                        pincode = pincode_raw

                    objs.append(
                        PincodeMaster(
                            pincode=pincode,
                            district=clean_val(row.get("district")),
                            statename=clean_val(row.get("statename")),
                            latitude=clean_val(row.get("latitude")),
                            longitude=clean_val(row.get("longitude")),
                            circlename=clean_val(row.get("circlename")),
                            regionname=clean_val(row.get("regionname")),
                            divisionname=clean_val(row.get("divisionname")),
                        )
                    )
                
                # Bulk create objects in chunks
                PincodeMaster.objects.bulk_create(objs, batch_size=1000)
                count = len(objs)
            else:
                # Update or create path
                for _, row in df.iterrows():
                    pincode_raw = clean_val(row.get("pincode"))
                    if not pincode_raw:
                        skipped += 1
                        continue

                    if pincode_raw.isdigit():
                        pincode = f"{int(pincode_raw):06d}"
                    else:
                        pincode = pincode_raw

                    defaults = {
                        "district": clean_val(row.get("district")),
                        "statename": clean_val(row.get("statename")),
                        "latitude": clean_val(row.get("latitude")),
                        "longitude": clean_val(row.get("longitude")),
                        "circlename": clean_val(row.get("circlename")),
                        "regionname": clean_val(row.get("regionname")),
                        "divisionname": clean_val(row.get("divisionname")),
                    }

                    PincodeMaster.objects.update_or_create(pincode=pincode, defaults=defaults)
                    count += 1
                    if count % 1000 == 0:
                        self.stdout.write(self.style.NOTICE(f"Processed {count} rows..."))

            self.stdout.write(
                self.style.SUCCESS(
                    f"Import complete! Result: Imported/Updated={count}, Skipped={skipped}"
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during import: {str(e)}"))
            import traceback
            traceback.print_exc()
