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
        else:
            print("================== ERROR IN :clean_isActive ==================")
            print(raw_data)

    def clean_phone_no(self, raw_phone):
        phone = self.clean_str_field(raw_phone)
        phone = "+91" + phone
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
        split_name = name.rsplit(" ", 1)
        print(split_name)
        if len(split_name)==1:
            return split_name[0], None
        return split_name[0], split_name[1]

#utils = UploadExcelToDB()


# upload_excel_to_db_users()
# upload_excel_to_db_branch()
# upload_excel_to_db_branch_user_mapping()
#
#
# print("===== user_ser_error =====")
# print(utils.user_ser_error)
# print("===== branch_ser_error =====")
# print(utils.branch_ser_error)
# print("===== branch_user_mapping_ser_error =====")
# print(utils.branch_user_mapping_ser_error)
# print("===== script_stats =====")
# print(utils.script_stats)
# print("===== bum_no_branch_id_deteted =====")
# print(utils.bum_absent_branch)



#python3 manage.py shell
#exec(open('excel_script/2023_05_20/upload_data_2023_05_20.py').read())