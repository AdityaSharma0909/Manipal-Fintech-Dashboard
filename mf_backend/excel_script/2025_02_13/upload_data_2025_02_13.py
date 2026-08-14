import pandas as pd
import datetime as dt
import random
import math

from django.db import transaction
from django.contrib.auth.hashers import make_password

from users.models import User
from users.serializers import UserModelSerializer
from utils.constants import ROLES, ADDRESS_TYPE, PLATFORM_TYPE, RESENDITIAL_OWNERSHIP
from users.service.userService import UserService
from branch.models import Branch, BranchUserMapping
from branch.serializers import CreateBranchSerializer, BranchUserMappingModelSerializer

default_password = "Radian@123"

excel_file = pd.ExcelFile("./excel_script/2025_02_13/sheet.xlsx")
sheet1 = "New List"

class UploadExcelToDB:
    def __init__(self):
        self.script_stats = {
            "user_created": 0,
            "user_ser_error": 0,
            "updated_user": 0,
            "updated_branch": 0,
            "branch_created": 0,
            "branch_ser_error": 0,
            "branch_user_mapping_created": 0,
            "branch_user_mapping_ser_error": 0,
            "bum_no_branch_id_deteted": 0,  # bum = branch user mapping
            "new_users_data": [],
            "updated_users_data": [],
            "new_branch_mapping_data": [],
        }

        self.user_ser_error = {}
        self.branch_ser_error = {}
        self.branch_user_mapping_ser_error = {}
        self.bum_absent_branch = {}

    def clean_str_field(self, data):
        data = str(data)
        data = data.replace('"', "")
        data = data.replace("'", "")
        data = data.strip()
        return data
    
    def clean_float_field(self, data):
        if (
            data
            and data != "Nan"
            and data != "nan"
            and not math.isnan(data)
            and data != ""
            and type(data) == float
        ):
            data = int(data)
        data = str(data)
        if ".0" in data:
            data = data.rstrip(".0")
        return data
    
    def replace_role(self, raw_role, raw_product):
        processed_role = self.clean_str_field(raw_role).lower()
        processed_product = self.clean_str_field(raw_product).lower()

        print(f"Processed Product: {processed_product}")
        print(f"Processed Role: {processed_role}")

        if "hl" in processed_product and ("sales manager" in processed_role or "relationship officer" in processed_role or "relationship manager" in processed_role or "team leader" in processed_role or "cluster manager" in processed_role):
            output_role = ROLES.RELATIONSHIP_MANAGER.value
        elif "il" in processed_product and ("sales manager" in processed_role or "team leader" in processed_role or "state head" in processed_role or "backend operations" in processed_role or "relationship manager" in processed_role or "relationship executive" in processed_role or "loan manager" in processed_role):
            output_role = ROLES.RELATIONSHIP_MANAGER.value
        elif "il-be" in processed_product and ("credit manager" in processed_role or "credit analyst" in processed_role or "associate" in processed_role):
            output_role = ROLES.CREDIT_MANAGER.value
        elif "il-be" in processed_product and "backend operations" in processed_role:
            output_role = ROLES.CPC.value
        elif "gl" in processed_product and ("senior loan manager" in processed_role or "trainee loan manager" in processed_role or "loan manager" in processed_role or "cluster manager" in processed_role):
            output_role = ROLES.LOAN_OFFICER.value
        elif "gl" in processed_product and "branch manager" in processed_role:
            output_role = ROLES.BRANCH_MANAGER.value
        elif "gl" in processed_product and ("operation manager" in processed_role or "associate" in processed_role):
            output_role = ROLES.CPC.value
        elif "il-be" in processed_product and ("team leader" in processed_role or "cluster head" in processed_role):
            output_role = ROLES.CREDIT_OFFICER.value
        else:
            print("ELSE - No matching role found")
            output_role = ROLES.BRANCH_MANAGER.value

        return output_role
    
    def clean_isActive(self, raw_data):
        data = self.clean_str_field(raw_data)
        data = data.lower()

        if data == "inactive":
            return False
        elif data == "active":
            return True
        elif data == "subbatical":
            return True
        elif data == "0":
            return True
        else:
            print("================== ERROR IN :clean_isActive ==================")
            print(raw_data)

    def clean_phone_no(self, raw_phone):
        # Convert integer to string
        raw_phone_str = str(raw_phone)
        # Extract only digits from the raw_phone
        digits_only = "".join(char for char in raw_phone_str if str.isdigit(char))
        # Take the first 10 digits
        first_10_digits = digits_only[:10]
        # Add the country code if needed
        phone = "+91" + first_10_digits

        return phone

    def clean_date(self, raw_date):
        date = self.clean_str_field(raw_date)
        # date = date.replace("/","-")
        date = date.replace(" 00:00:00", "")
        if date.lower() == "nat":
            return None
        if date.lower() == "nan":
            return None

        # print(" ========== Date ========== ")
        # print(date)
        # print(raw_date)
        return date
    
    def random_phone_num_generator(self):
        first = str(random.randint(100, 999))
        second = str(random.randint(1, 888)).zfill(3)
        last = str(random.randint(1, 9998)).zfill(4)
        while last in ["1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888"]:
            last = str(random.randint(1, 9998)).zfill(4)
        number = "989" + second + last
        # return number[0:10]
        number = "+91" + number[0:10]
        return number
    
    def get_employee_from_id(self, emp_id):
        emp_id = self.clean_str_field(emp_id)
        emp_id = emp_id.replace(".0", "")
        emp_id = emp_id.zfill(5)
        # print("===== get_employee_from_id =====")
        # print(emp_id)

        if emp_id == None:
            return None

        user = User.objects.filter(employee_id=emp_id)
        if user.count() > 0:
            # print(str(user[0].user_id))
            # input("Enter any Key....")
            return str(user[0].user_id)
        else:
            # print(None)
            # input("Enter any Key....")
            return None

    def get_branch_from_id(self, branch_code):
        branch_code = self.clean_str_field(branch_code)
        branch_code = branch_code.replace(".0", "")
        branch_code = branch_code
        if branch_code == None:
            return None

        branch = Branch.objects.filter(branch_code=branch_code)
        if branch.count() > 0:
            return str(branch[0].branch_id)
        else:
            return None

    def get_name(self, name):
        name = self.clean_str_field(name)
        split_name = name.rsplit(" ", 1)
        # print(split_name)
        if len(split_name) == 1:
            return split_name[0], None
        return split_name[0], split_name[1]


utils = UploadExcelToDB()


def upload_excel_to_db_users():
    # try:
    df_employee = pd.read_excel(excel_file, sheet1)

    # all_phone_nos = df_employee["Contact Number 1"]
    all_emp_ids = df_employee["Employee ID"]
    print("Columns: ", df_employee.columns)
    print(df_employee["Product"])

    for index, emp_id in enumerate(all_emp_ids):
        with transaction.atomic():
            first_name, last_name = utils.get_name(df_employee["Employee Name"][index])
            emp_id = utils.clean_float_field(emp_id)
            employee_id = utils.clean_str_field(emp_id).zfill(5)
            phone = utils.clean_phone_no(df_employee["Contact Number 1"][index])
            user_data = {
                "phone": phone,
                "role": utils.replace_role(
                    df_employee["Role"][index],
                    df_employee["Product"][index],
                    ),

                "designation": utils.clean_str_field(df_employee["Role"][index]),
                "aadhar_no": utils.clean_str_field(
                    df_employee["Aadhaar Number"][index]
                ),
                "pan_no": utils.clean_str_field(df_employee["PAN Number"][index]),
                "employee_id": employee_id,
                "date_of_joining": utils.clean_date(
                    df_employee["Date of Joining"][index]
                ),
                "is_active": utils.clean_isActive(df_employee["Status"][index]),
                # "email": utils.clean_str_field(df_employee["Email id"][index]),
                # "username": UserService().generate_username()
                "username": employee_id,
            }
            if first_name:
                user_data["first_name"] = first_name
            if last_name:
                user_data["last_name"] = last_name

            print("===== user_data =====")
            print(
                employee_id + ": " + first_name
                if first_name
                else "" + " " + last_name if last_name else ""
            )
            print(user_data)
            print("\n")

            dbUser = User.objects.filter(username=employee_id)
            if len(dbUser) == 0:
                print("Inserting user ... \n")
                user_ser = UserModelSerializer(data=user_data)
                if user_ser.is_valid():
                    user_ser.save()
                    user = User.objects.get(phone=user_data["phone"])
                    user.set_password(default_password)
                    user.save()
                    utils.script_stats['new_users_data'].append(user_ser.data['user_id'])

                    utils.script_stats["user_created"] += 1
                else:
                    utils.user_ser_error[phone] = user_ser.errors
                    utils.script_stats["user_ser_error"] += 1
            else:
                print("Updating user ... \n")
                dbUser.update(**user_data)
                utils.script_stats["updated_user"] += 1
                # utils.script_stats['updated_users_data'].append(dbUser)



def upload_excel_to_db_branch_user_mapping():
    df_employee = pd.read_excel(excel_file, sheet1)

    # all_phone_nos = df_employee["Contact Number 1"]
    all_emp_ids = df_employee["Employee ID"]

    for index, emp_id in enumerate(all_emp_ids):
        with transaction.atomic():
            branch_code = df_employee["Branch code"][index]
            print("branch_code: ", branch_code)
            branch_id = utils.get_branch_from_id(branch_code)
            print(branch_id)
            if not branch_id:
                print("bum_no_branch_id_deteted")
                print(df_employee["Branch code"][index])
                utils.script_stats["bum_no_branch_id_deteted"] += 1
                # input("Enter any KEy...")
                utils.bum_absent_branch[branch_code] = (
                    utils.bum_absent_branch.get(branch_code, 0) + 1
                )

                continue

            branch_user_mapping_data = {
                "user": utils.get_employee_from_id(emp_id),
                "branch": branch_id,
                "source_id": 500,
            }

            print("===== branch_user_mapping_data =====")
            print(branch_user_mapping_data)
            print("\n\n")

            branchUserMap = BranchUserMapping.objects.filter(
                branch__branch_id=branch_id,
                user=utils.get_employee_from_id(df_employee["Employee ID"][index]),
            )

            if len(branchUserMap) == 0:
                bum_ser = BranchUserMappingModelSerializer(
                    data=branch_user_mapping_data
                )
                if bum_ser.is_valid():
                    bum_ser.save()
                    utils.script_stats["branch_user_mapping_created"] += 1
                    utils.script_stats['new_branch_mapping_data'].append(bum_ser.data['user'])
                else:
                    phone = utils.clean_phone_no(df_employee["Contact Number 1"][index])
                    utils.branch_user_mapping_ser_error[phone] = bum_ser.errors
                    utils.script_stats["branch_user_mapping_ser_error"] += 1
            else:
                print("Branch User Mapping already exists")


# upload_excel_to_db_branch()
upload_excel_to_db_users()
upload_excel_to_db_branch_user_mapping()


print("\n\n\n")
print("===== user_ser_error =====")
print(utils.user_ser_error)
print("===== branch_ser_error =====")
print(utils.branch_ser_error)
print("===== branch_user_mapping_ser_error =====")
print(utils.branch_user_mapping_ser_error)
print("===== script_stats =====")
print(utils.script_stats)
print("===== bum_no_branch_id_deteted =====")
print(utils.bum_absent_branch)
print("\n\n\n")

"""
python3 manage.py shell
exec(open('excel_script/2025_02_13/upload_data_2025_02_13.py').read())
"""