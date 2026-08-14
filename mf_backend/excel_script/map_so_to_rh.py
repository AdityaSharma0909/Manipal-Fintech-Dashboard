import pandas as pd
from django.db import transaction
from users.models import User

excel_file_path = "./Filed Sales Employee list.xlsx"

class MapSOToRH:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.stats = {
            "so_found": 0,
            "so_not_found": 0,
            "rh_found_and_mapped": 0,
            "rh_not_found": 0,
            "skipped_empty_rh": 0,
            "failed_saves": 0,
        }

    def clean_emp_id(self, val):
        if pd.isna(val) or val is None:
            return None
        val_str = str(val).strip()
        if val_str in ["nan", "", "-", "NaN", "Nat"]:
            return None
        if ".0" in val_str:
            val_str = val_str.split(".0")[0]
        return val_str

    def run(self):
        print(f"Reading file: {excel_file_path}")
        try:
            # header=2 sets the columns to the third row ('SO Name ', ' SO Employee ID ', etc.)
            df = pd.read_excel(excel_file_path, header=2)
        except Exception as e:
            print(f"Error reading excel file: {str(e)}")
            return

        # Strip whitespaces from column names
        df.columns = df.columns.str.strip()
        print("Cleaned Columns:", df.columns.tolist())
        print(f"Found {len(df)} rows in excel.")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE MAP'}")
        print("=" * 70)

        for index, row in df.iterrows():
            so_name = str(row.get("SO Name")).strip()
            so_emp_id = self.clean_emp_id(row.get("SO Employee ID"))
            rh_name = str(row.get("RH Name")).strip()
            rh_emp_id = self.clean_emp_id(row.get("RH Employee ID"))

            if not so_emp_id:
                # Skip rows with no SO Employee ID
                continue

            # Look up SO user in the database
            so_user = User.objects.filter(employee_id=so_emp_id).first()
            if not so_user:
                print(f"[SO NOT FOUND] Row {index + 3}: SO '{so_name}' (Emp ID: {so_emp_id}) does not exist in DB.")
                self.stats["so_not_found"] += 1
                continue

            self.stats["so_found"] += 1

            if not rh_emp_id:
                print(f"[NO RH SPECIFIED] Row {index + 3}: SO '{so_name}' (Emp ID: {so_emp_id}) has no RH assigned in sheet.")
                self.stats["skipped_empty_rh"] += 1
                continue

            # Look up RH user in the database
            rh_user = User.objects.filter(employee_id=rh_emp_id).first()
            if not rh_user:
                print(f"[RH NOT FOUND] Row {index + 3}: RH '{rh_name}' (Emp ID: {rh_emp_id}) not found for SO '{so_name}' (Emp ID: {so_emp_id}).")
                self.stats["rh_not_found"] += 1
                continue

            # If both exist, map them
            print(f"[MAP] SO '{so_user.first_name} {so_user.last_name}' (Emp ID: {so_emp_id}) -> RH '{rh_user.first_name} {rh_user.last_name}' (Emp ID: {rh_emp_id})")
            
            if not self.dry_run:
                try:
                    with transaction.atomic():
                        so_user.assign_so = rh_user
                        so_user.save()
                        print(f"  -> Successfully mapped.")
                        self.stats["rh_found_and_mapped"] += 1
                except Exception as ex:
                    print(f"  -> Failed to save: {str(ex)}")
                    self.stats["failed_saves"] += 1
            else:
                self.stats["rh_found_and_mapped"] += 1

        print("=" * 70)
        print("Summary of execution:")
        for k, v in self.stats.items():
            print(f"  {k.replace('_', ' ').capitalize()}: {v}")
        print("=" * 70)

# To run the script in shell:
# 1. Dry-run:
#    exec(open('excel_script/map_so_to_rh.py').read()); MapSOToRH(dry_run=True).run()
# 2. Live Run:
#    exec(open('excel_script/map_so_to_rh.py').read()); MapSOToRH(dry_run=False).run()
