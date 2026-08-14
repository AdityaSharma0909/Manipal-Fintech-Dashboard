import pandas as pd
import datetime as dt
import math
from django.db import transaction
from users.models import User
from users.serializers import UserModelSerializer
from utils.constants import ROLES, DESIGNATION

default_password = "Radian@123"
excel_file_path = "./Book2.xlsx"

class UploadRHUsers:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.stats = {
            "created": 0,
            "updated": 0,
            "failed": 0,
            "skipped_phone_conflict": 0,
        }

    def clean_phone_no(self, raw_phone):
        if pd.isna(raw_phone) or not raw_phone:
            return None
        raw_phone_str = str(raw_phone)
        # Extract digits only
        digits = "".join(char for char in raw_phone_str if char.isdigit())
        # Get the last 10 digits
        last_10 = digits[-10:]
        if len(last_10) < 10:
            return None
        return "+91" + last_10

    def clean_date(self, raw_date):
        if pd.isna(raw_date) or not raw_date:
            return None
        if isinstance(raw_date, (dt.datetime, dt.date, pd.Timestamp)):
            return raw_date.strftime("%Y-%m-%d")
        
        raw_date_str = str(raw_date).strip()
        if raw_date_str.lower() in ["nan", "nat", ""]:
            return None
        try:
            parsed = pd.to_datetime(raw_date_str)
            return parsed.strftime("%Y-%m-%d")
        except Exception:
            return None

    def clean_str(self, val):
        if pd.isna(val) or val is None:
            return None
        val_str = str(val).strip()
        if val_str.lower() in ["nan", ""]:
            return None
        return val_str

    def clean_pincode(self, raw_pincode):
        if pd.isna(raw_pincode) or not raw_pincode:
            return None
        raw_pin_str = str(raw_pincode).strip()
        if ".0" in raw_pin_str:
            raw_pin_str = raw_pin_str.split(".0")[0]
        digits = "".join(c for c in raw_pin_str if c.isdigit())
        if len(digits) == 6:
            return digits
        return None

    def run(self):
        print(f"Reading file: {excel_file_path}")
        try:
            df = pd.read_excel(excel_file_path)
        except Exception as e:
            print(f"Error reading excel file: {str(e)}")
            return

        print(f"Found {len(df)} rows in excel.")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE UPLOAD'}")
        print("=" * 60)

        for index, row in df.iterrows():
            emp_id_raw = row.get("Emp ID")
            if pd.isna(emp_id_raw) or not emp_id_raw:
                print(f"Row {index}: Skipping due to missing Emp ID")
                continue

            # Parse employee ID as simple string integer representation
            try:
                emp_id_str = str(int(float(emp_id_raw)))
            except ValueError:
                emp_id_str = str(emp_id_raw).strip()

            phone_raw = row.get("Phone number")
            phone = self.clean_phone_no(phone_raw)
            if not phone:
                print(f"Row {index} (Emp ID: {emp_id_str}): Skipping due to invalid phone number: {phone_raw}")
                self.stats["failed"] += 1
                continue

            # Concatenate name columns
            name_parts = []
            for col in ["First name", "Last name", "Unnamed: 4", "Unnamed: 5"]:
                val = row.get(col)
                cleaned_val = self.clean_str(val)
                if cleaned_val:
                    name_parts.append(cleaned_val)
            
            if name_parts:
                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:])
            else:
                first_name = "RH"
                last_name = f"User_{emp_id_str}"

            email = self.clean_str(row.get("email id"))
            doj = self.clean_date(row.get("date of joining"))
            pincode = self.clean_pincode(row.get("pincode"))
            district = self.clean_str(row.get("District"))
            state = self.clean_str(row.get("State"))

            # Build user data dictionary
            user_data = {
                "username": emp_id_str,
                "phone": phone,
                "role": ROLES.REGIONAL_HEAD.value,
                "designation": DESIGNATION.RH.value,
                "employee_id": emp_id_str,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
            }

            if email:
                user_data["email"] = email
            if doj:
                user_data["date_of_joining"] = doj
            if pincode:
                user_data["pincode"] = pincode
            if district:
                user_data["district"] = district
            if state:
                user_data["state"] = state

            # Check if user with this employee_id exists
            existing_user_by_emp = User.objects.filter(employee_id=emp_id_str).first()
            # Check if user with this phone exists
            existing_user_by_phone = User.objects.filter(phone=phone).first()

            if existing_user_by_emp:
                # If they exist, check if there's a phone mismatch
                if existing_user_by_phone and existing_user_by_phone.employee_id != emp_id_str:
                    print(f"[CONFLICT] Emp ID {emp_id_str} exists but phone {phone} is already registered to Emp ID {existing_user_by_phone.employee_id}. Skipping.")
                    self.stats["skipped_phone_conflict"] += 1
                    continue

                print(f"[UPDATE] Emp ID {emp_id_str} ({first_name} {last_name}):")
                print(f"  Phone: {phone}, Email: {email}, State: {state}, District: {district}")
                if not self.dry_run:
                    try:
                        with transaction.atomic():
                            # Update existing record using serializer
                            serializer = UserModelSerializer(existing_user_by_emp, data=user_data, partial=True)
                            if serializer.is_valid():
                                serializer.save()
                                print(f"  -> Successfully updated.")
                                self.stats["updated"] += 1
                            else:
                                print(f"  -> Update Failed! Errors: {serializer.errors}")
                                self.stats["failed"] += 1
                    except Exception as ex:
                        print(f"  -> Transaction failed: {str(ex)}")
                        self.stats["failed"] += 1
                else:
                    self.stats["updated"] += 1

            elif existing_user_by_phone:
                # Phone matches but employee_id does not
                print(f"[CONFLICT] Phone {phone} already belongs to Emp ID {existing_user_by_phone.employee_id} (Requested: {emp_id_str}). Skipping.")
                self.stats["skipped_phone_conflict"] += 1
                continue

            else:
                # New user creation
                print(f"[CREATE] Emp ID {emp_id_str} ({first_name} {last_name}):")
                print(f"  Phone: {phone}, Email: {email}, State: {state}, District: {district}")
                if not self.dry_run:
                    try:
                        with transaction.atomic():
                            serializer = UserModelSerializer(data=user_data)
                            if serializer.is_valid():
                                user = serializer.save()
                                user.set_password(default_password)
                                user.save()
                                print(f"  -> Successfully created with default password '{default_password}'.")
                                self.stats["created"] += 1
                            else:
                                print(f"  -> Creation Failed! Errors: {serializer.errors}")
                                self.stats["failed"] += 1
                    except Exception as ex:
                        print(f"  -> Transaction failed: {str(ex)}")
                        self.stats["failed"] += 1
                else:
                    self.stats["created"] += 1

        print("=" * 60)
        print("Summary of execution:")
        for k, v in self.stats.items():
            print(f"  {k.replace('_', ' ').capitalize()}: {v}")
        print("=" * 60)
