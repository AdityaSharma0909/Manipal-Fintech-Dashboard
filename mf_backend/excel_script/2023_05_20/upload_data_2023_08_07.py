    # Loan Manager - Loan Manager / Senior Loan Manager
    # CPC - CPC Manager
    # Everyone else BM

    # Extra Requirements:
    # pip install pandas==2.0.1
    # pip install openpyxl==3.1.2

import pandas as pd
import datetime as dt
import random
import os

from django.db import transaction
from django.contrib.auth.hashers import make_password

from users.models import User
from users.serializers import UserModelSerializer
from utils.constants import ROLES, ADDRESS_TYPE, PLATFORM_TYPE, RESENDITIAL_OWNERSHIP
from users.service.userService import UserService
from branch.models import Branch, BranchUserMapping
from branch.serializers import CreateBranchSerializer, BranchUserMappingModelSerializer

default_password = "Radian@123"
# default_password = make_password(default_password)

excel_file = pd.ExcelFile('./excel_script/2023_05_20/Employee_&_Branch_details_07-08-2023.xlsx')
sheet1 = "Employee Details"
sheet2 = "CPC Team "
sheet3 = "Branch wise"



class UploadExcelToDB():
    def __init__(self):
        self.script_stats = {
            "user_created": 0,
            "user_ser_error": 0,

            "branch_created": 0,
            "branch_ser_error": 0,

            "branch_user_mapping_created": 0,
            "branch_user_mapping_ser_error": 0,
            "bum_no_branch_id_deteted": 0, #bum = branch user mapping

         }

        self.user_ser_error = {}
        self.branch_ser_error = {}
        self.branch_user_mapping_ser_error = {}
        self.bum_absent_branch = {}
    
    def clean_str_field(self, data):
        data = str(data)
        data = data.replace("\"","")
        data = data.replace("\'","")
        data = data.strip()
        return data

    def replace_role(self, raw_role):
        processed_role = self.clean_str_field(raw_role)
        processed_role = processed_role.lower()

        # if processed_role == "loan manager" or processed_role=="senior loan manager":
        #     output_role = ROLES.LOAN_OFFICER.value
        # elif processed_role == "cpc manager" or processed_role=="assistant manager (cpc admin)":
        #     output_role = ROLES.CPC.value
        # else:
        #     output_role = ROLES.BRANCH_MANAGER.value

        if "loan" in processed_role and "manager" in processed_role:
            output_role = ROLES.LOAN_OFFICER.value
        elif "cpc" in processed_role:
            output_role = ROLES.CPC.value
        elif "assistant" in processed_role and "branch" in processed_role:
            output_role = ROLES.ASSISTANT_BRANCH_MANAGER.value
        elif "branch" in processed_role:
            output_role = ROLES.BRANCH_MANAGER.value
        elif "cluster" in processed_role:
            output_role = ROLES.CLUSTER_MANAGER.value
        elif "regional" in processed_role:
            output_role = ROLES.REGIONAL_HEAD.value
        else:
            output_role = ROLES.LOAN_OFFICER.value
        
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
        elif data == "":
            return True
        elif data == "Leave Without pay":
            return True
        else:
            return False

            # print("================== ERROR IN :clean_isActive ==================")
            # print(raw_data)

    def clean_phone_no(self, raw_phone):
        phone = self.clean_str_field(raw_phone)
        phone = "+91" + phone
        phone = phone.split('.')[0]
        print("phone ::::: ")
        print(phone)
        return phone
    
    def clean_date(self, raw_date):
        date = self.clean_str_field(raw_date)
        # date = date.replace("/","-")
        date = date.replace(" 00:00:00","")
        if date.lower() == "nat":
            return None
        
        # print(" ========== Date ========== ")
        # print(date)
        # print(raw_date)
        return date
    
    def random_phone_num_generator(self):
        first = str(random.randint(100, 999))
        second = str(random.randint(1, 888)).zfill(3)
        last = (str(random.randint(1, 9998)).zfill(4))
        while last in ['1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888']:
            last = (str(random.randint(1, 9998)).zfill(4))
        number = '989'+second+last
        # return number[0:10]
        number = "+91" + number[0:10]
        return number
    
    def get_employee_from_id(self, emp_id):
        emp_id = self.clean_str_field(emp_id)
        emp_id = emp_id.replace(".0","")
        emp_id = emp_id.zfill(5)
        # print("===== get_employee_from_id =====")
        # print(emp_id)

        
        if emp_id == None:
            return None
        
        user = User.objects.filter(employee_id=emp_id)
        if user.count()>0:
            # print(str(user[0].user_id))
            # input("Enter any Key....")
            return str(user[0].user_id)
        else:
            # print(None)
            # input("Enter any Key....")
            return None
    def get_branch_from_id(self, branch_code):
        branch_code = self.clean_str_field(branch_code)
        branch_code = branch_code.replace(".0","")
        branch_code = branch_code
        if branch_code == None:
            return None
        
        branch = Branch.objects.filter(branch_code=branch_code)
        if branch.count()>0:
            return str(branch[0].branch_id)
        else:
            return None
    

    def get_name(self, name):
        name = self.clean_str_field(name)
        print("name")
        print(name)
        split_name = name.rsplit(" ", 1)
        print(split_name)
        if len(split_name)==1:
            return split_name[0], None
        return split_name[0], split_name[1]

utils = UploadExcelToDB()

def upload_excel_to_db_users():
    df_employee = pd.read_excel(excel_file, sheet1)

    # all_phone_nos = df_employee["Mobile No "]
    all_phone_nos = df_employee.iloc[:,7] # Mobile number

    for index, each_phone_no in enumerate(all_phone_nos):
        with transaction.atomic():

            # first_name, last_name = utils.get_name(df_employee["Employee Name "][index])
            first_name, last_name = utils.get_name(df_employee.iloc[:,1][index]) # Employee Name
            employee_id = utils.clean_str_field(df_employee.iloc[:,0][index]).zfill(5) # Employee Id
            user_data = {
                "phone": utils.clean_phone_no(each_phone_no),

                "role": utils.replace_role( df_employee.iloc[:,2][index]), # Role
                "designation": utils.clean_str_field( df_employee.iloc[:,2][index] ), # Role
                "aadhar_no": utils.clean_str_field(df_employee.iloc[:,6][index]),
                "pan_no": utils.clean_str_field(df_employee.iloc[:,5][index]),
                "employee_id": employee_id,
                # "date_of_joining": utils.clean_date(df_employee["DOJ "][index]),
                "is_active": utils.clean_isActive(df_employee.iloc[:,9][index]),

                # "username": UserService().generate_username()
                "username": employee_id,
            }

            if first_name:
                user_data["first_name"] = first_name
            if last_name:
                user_data["last_name"] = last_name

            print("===== user_data =====")
            print(user_data)

            user_ser = UserModelSerializer(data = user_data)
            if user_ser.is_valid():
                user_ser.save()
                user = User.objects.get(phone= user_data["phone"])
                user.set_password(default_password)
                user.save()
                
                utils.script_stats["user_created"] += 1
            else:
                utils.user_ser_error[each_phone_no] = user_ser.errors
                utils.script_stats["user_ser_error"] += 1

            # if index>11:
            #     break


def upload_excel_to_db_branch():
    df_branch = pd.read_excel(excel_file, sheet3)
    all_branch_code = df_branch.iloc[:,4]


    for index, each_branch_code in enumerate(all_branch_code):
        with transaction.atomic():
            branch_data = {
                    "branch_code":utils.clean_str_field( df_branch.iloc[:,4][index] ),
                    "address":utils.clean_str_field( df_branch.iloc[:,2][index] ),
                    "opening_date":utils.clean_date( df_branch.iloc[:,3][index] ),
                    "assistant_bm":utils.get_employee_from_id( df_branch.iloc[:,5][index] ),
                    "cluster_manager":utils.get_employee_from_id( df_branch.iloc[:,9][index] ),
                    "regional_head":utils.get_employee_from_id( df_branch.iloc[:,11][index] ),
                    "branch_manager":utils.get_employee_from_id( df_branch.iloc[:,7][index] ),
                    "state":utils.clean_str_field( df_branch.iloc[:,0][index] ),
                    "branch_name":utils.clean_str_field( df_branch.iloc[:,1][index] ),
                    # "stamp_duty_percent ":utils.clean_str_field( df_branch[""][index] ),
                    # "stamp_duty_amount ":utils.clean_str_field( df_branch[""][index] ),
                    # "stamp_duty_minimum_amount_eligibility ":utils.clean_str_field( df_branch[""][index] ),
                    # "phone": utils.clean_str_field( df_branch[""][index] ),
                    "phone": utils.random_phone_num_generator(), # TODO Need to make this null=True, blank=True in models
            }

            print("===== Branch =====")
            print(branch_data)

            branch_ser = CreateBranchSerializer(data = branch_data)
            if branch_ser.is_valid():
                branch_ser.save()
                utils.script_stats["branch_created"] += 1
            else:
                utils.branch_ser_error[each_branch_code] = branch_ser.errors
                utils.script_stats["branch_ser_error"] += 1

def upload_excel_to_db_branch_user_mapping():
    df_employee = pd.read_excel(excel_file, sheet1)

    all_phone_nos = df_employee["Mobile No "]

    for index, each_phone_no in enumerate(all_phone_nos):
        with transaction.atomic():
            branch_code = df_employee["Branch Code "][index]
            branch_id = utils.get_branch_from_id( branch_code )
            print(branch_id)
            if not branch_id:
                print("bum_no_branch_id_deteted")
                print(df_employee["Branch Code "][index])
                utils.script_stats["bum_no_branch_id_deteted"] += 1
                # input("Enter any KEy...")
                utils.bum_absent_branch[branch_code] = utils.bum_absent_branch.get(branch_code,0)+1
                
                continue

            branch_user_mapping_data = {                
                "user": utils.get_employee_from_id( df_employee["Employee ID"][index] ),
                "branch": branch_id,
                "source_id": 500
            }

            print("===== branch_user_mapping_data =====")
            print(branch_user_mapping_data)

            bum_ser = BranchUserMappingModelSerializer(data = branch_user_mapping_data)
            if bum_ser.is_valid():
                bum_ser.save()
                utils.script_stats["branch_user_mapping_created"] += 1
            else:
                utils.branch_user_mapping_ser_error[each_phone_no] = bum_ser.errors
                utils.script_stats["branch_user_mapping_ser_error"] += 1


upload_excel_to_db_users()
upload_excel_to_db_branch()
upload_excel_to_db_branch_user_mapping()


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



# python3 manage.py shell
# exec(open('excel_script/2023_05_20/upload_data_2023_08_07.py').read())