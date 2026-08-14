from django.db import transaction

from branch.serializers import CreateBranchSerializer, BranchUserMappingModelSerializer
from users.models import User
from users.serializers import UserModelSerializer
from utility.initial_setup.upload_data_2023_05_20 import UploadExcelToDB
import pandas as pd

class PopulateEmployeeData:
    utils=UploadExcelToDB()
    excel_file = pd.ExcelFile('./excel_script/2023_05_20/Employee_and_Branch_details.xlsx')
    employees_sheet = "Employee Details "
    cpc_sheet = "CPC Team "
    branch_sheet = "Branch Wise "
    default_password = "Radian@123"
    def upload_excel_to_db_users(self):
        df_employee = pd.read_excel(self.excel_file, self.employees_sheet)

        all_phone_nos = df_employee["Mobile No "]

        for index, each_phone_no in enumerate(all_phone_nos):
            with transaction.atomic():

                first_name, last_name = self.utils.get_name(df_employee["Employee Name "][index])
                employee_id = self.utils.clean_str_field(df_employee["Employee ID"][index]).zfill(5)
                user_data = {
                    "phone": self.utils.clean_phone_no(each_phone_no),

                    "role": self.utils.replace_role(df_employee["Designation/Job Role "][index]),
                    "designation": self.utils.clean_str_field(df_employee["Designation/Job Role "][index]),
                    "aadhar_no": self.utils.clean_str_field(df_employee["Aadhaar No"][index]),
                    "pan_no": self.utils.clean_str_field(df_employee["Pan No "][index]),
                    "employee_id": employee_id,
                    "date_of_joining": self.utils.clean_date(df_employee["DOJ "][index]),
                    "is_active": self.utils.clean_isActive(df_employee["Status "][index]),

                    # "username": UserService().generate_username()
                    "username": employee_id,
                }
                if first_name:
                    user_data["first_name"] = first_name
                if last_name:
                    user_data["last_name"] = last_name

                print("===== user_data =====")
                print(user_data)

                user_ser = UserModelSerializer(data=user_data)
                if user_ser.is_valid():
                    user_ser.save()
                    user = User.objects.get(phone=user_data["phone"])
                    user.set_password(self.default_password)
                    user.save()

                    self.utils.script_stats["user_created"] += 1
                else:
                    self.utils.user_ser_error[each_phone_no] = user_ser.errors
                    self.utils.script_stats["user_ser_error"] += 1

                # if index>11:
                #     break

    def upload_excel_to_db_branch(self):
        df_branch = pd.read_excel(self.excel_file, self.branch_sheet)
        all_branch_code = df_branch[" Branch code"]

        for index, each_branch_code in enumerate(all_branch_code):
            with transaction.atomic():
                branch_data = {
                    "branch_code": self.utils.clean_str_field(df_branch[" Branch code"][index]),
                    "address": self.utils.clean_str_field(df_branch[" Address"][index]),
                    "opening_date": self.utils.clean_date(df_branch[" Opening Date"][index]),
                    "assistant_bm": self.utils.get_employee_from_id(df_branch["ABM Emp ID "][index]),
                    "cluster_manager": self.utils.get_employee_from_id(df_branch[" Cluster Emp  ID"][index]),
                    "regional_head": self.utils.get_employee_from_id(df_branch[" Regional Head"][index]),
                    "branch_manager": self.utils.get_employee_from_id(df_branch["BM  Emp ID "][index]),
                    "state": self.utils.clean_str_field(df_branch[" State"][index]),
                    "branch_name": self.utils.clean_str_field(df_branch[" Branch Name"][index]),
                    # "stamp_duty_percent ":self.utils.clean_str_field( df_branch[""][index] ),
                    # "stamp_duty_amount ":self.utils.clean_str_field( df_branch[""][index] ),
                    # "stamp_duty_minimum_amount_eligibility ":self.utils.clean_str_field( df_branch[""][index] ),
                    # "phone": self.utils.clean_str_field( df_branch[""][index] ),
                    "phone": self.utils.random_phone_num_generator(),
                    # TODO Need to make this null=True, blank=True in models
                }

                print("===== Branch =====")
                print(branch_data)

                branch_ser = CreateBranchSerializer(data=branch_data)
                if branch_ser.is_valid():
                    branch_ser.save()
                    self.utils.script_stats["branch_created"] += 1
                else:
                    self.utils.branch_ser_error[each_branch_code] = branch_ser.errors
                    self.utils.script_stats["branch_ser_error"] += 1

    def upload_excel_to_db_branch_user_mapping(self):
        df_employee = pd.read_excel(self.excel_file, self.employees_sheet)

        all_phone_nos = df_employee["Mobile No "]

        for index, each_phone_no in enumerate(all_phone_nos):
            with transaction.atomic():
                branch_code = df_employee["Branch Code "][index]
                branch_id = self.utils.get_branch_from_id(branch_code)
                print(branch_id)
                if not branch_id:
                    print("bum_no_branch_id_deteted")
                    print(df_employee["Branch Code "][index])
                    self.utils.script_stats["bum_no_branch_id_deteted"] += 1
                    # input("Enter any KEy...")
                    self.utils.bum_absent_branch[branch_code] = self.utils.bum_absent_branch.get(branch_code, 0) + 1

                    continue

                branch_user_mapping_data = {
                    "user": self.utils.get_employee_from_id(df_employee["Employee ID"][index]),
                    "branch": branch_id,
                    "source_id": 500
                }

                print("===== branch_user_mapping_data =====")
                print(branch_user_mapping_data)

                bum_ser = BranchUserMappingModelSerializer(data=branch_user_mapping_data)
                if bum_ser.is_valid():
                    bum_ser.save()
                    self.utils.script_stats["branch_user_mapping_created"] += 1
                else:
                    self.utils.branch_user_mapping_ser_error[each_phone_no] = bum_ser.errors
                    self.utils.script_stats["branch_user_mapping_ser_error"] += 1