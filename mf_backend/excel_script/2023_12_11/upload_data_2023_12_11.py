import pandas as pd
from branch.models import BranchUserMapping, Branch
from branch.serializers import BranchUserMappingModelSerializer
from users.models import User
from django.db import transaction
import traceback
import math



class UploadExcelToDB(): 
    def __init__(self):
        self.script_stats = {
            "user_error_count": 0,
            "cluster_branch_user_mapping_created": 0,
            "regional_branch_user_mapping_created": 0,
            "cluster_mapping_already_exists":0,
            "regional_mapping_already_exists": 0,
            "cluster_error":0,
            "regional_error":0,
            "bum_no_branch_id_deteted": 0,
        }


    def clean_str_field(self, data):
        data = str(data)
        data = data.replace("\"","")
        data = data.replace("\'","")
        data = data.strip()
        return data
    

    def clean_float_field(self, data):
        if data and data != 'Nan' and data != 'nan' and not math.isnan(data) and data != '' and type(data) == float:
            data = int(data)
        data = str(data)
        if ".0" in data:
            data = data.rstrip(".0") 
        return data
    
    def get_employee_from_id(self, emp_id):
        emp_id = self.clean_str_field(emp_id)
        emp_id = emp_id.replace(".0","")
        emp_id = emp_id.zfill(5)


        
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
    
utils = UploadExcelToDB()

def MappingScript():
    try:
        # Assuming your Excel file has 'Branch' and 'User' columns
        excel_file_path = pd.ExcelFile('./excel_script/2023_12_11/sheet.xlsx')
        
        # Load data from Excel file
        df = pd.read_excel(excel_file_path)

        # Iterate over branches
        all_branch_codes = df["Branch code"].unique()
        for branch_code in all_branch_codes:
            with transaction.atomic():
                branch_id = utils.get_branch_from_id(branch_code)
                print("Branch ID:", branch_id)

                if not branch_id:
                    print("bum_no_branch_id_deteted")
                    print("Branch Code:", branch_code)
                    utils.script_stats["bum_no_branch_id_deteted"] += 1
                    utils.bum_absent_branch[branch_code] = utils.bum_absent_branch.get(branch_code, 0) + 1
                    continue

                # Iterate over cluster employee IDs for the current branch
                cluster_emp_ids_for_branch = df[df["Branch code"] == branch_code]["Cluster Emp ID"]
                if not cluster_emp_ids_for_branch.empty:
                    for index, cluster_emp_id in enumerate(cluster_emp_ids_for_branch):
                        branch_user_mapping_data = {
                            "user": utils.get_employee_from_id(cluster_emp_id),
                            "branch": branch_id,
                            "source_id": 500
                        }

                        print("===== cluster_branch_user_mapping_data =====")
                        print(branch_user_mapping_data)
                        print("\n\n")

                        branchUserMap = BranchUserMapping.objects.filter(
                            branch__branch_id=branch_id,
                            user=utils.get_employee_from_id(cluster_emp_id)
                        )

                        if len(branchUserMap) == 0:
                            bum_ser = BranchUserMappingModelSerializer(data=branch_user_mapping_data)
                            if bum_ser.is_valid():
                                bum_ser.save()
                                utils.script_stats["cluster_branch_user_mapping_created"] += 1
                            else:
                                utils.script_stats["cluster_error"] += 1
                        else:
                            print("Cluster Branch User Mapping already exists")
                            utils.script_stats["cluster_mapping_already_exists"] += 1

                # Iterate over regional employee IDs for the current branch
                regional_emp_ids_for_branch = df[df["Branch code"] == branch_code]["Regional Emp ID"]
                if not regional_emp_ids_for_branch.empty:
                    for index, regional_emp_id in enumerate(regional_emp_ids_for_branch):
                        branch_user_mapping_data = {
                            "user": utils.get_employee_from_id(regional_emp_id),
                            "branch": branch_id,
                            "source_id": 500
                        }

                        print("===== regional_branch_user_mapping_data =====")
                        print(branch_user_mapping_data)
                        print("\n\n")

                        branchUserMap = BranchUserMapping.objects.filter(
                            branch__branch_id=branch_id,
                            user=utils.get_employee_from_id(regional_emp_id)
                        )

                        if len(branchUserMap) == 0:
                            bum_ser = BranchUserMappingModelSerializer(data=branch_user_mapping_data)
                            if bum_ser.is_valid():
                                bum_ser.save()
                                utils.script_stats["regional_branch_user_mapping_created"] += 1
                            else:
                                utils.script_stats["regional_error"] += 1
                        else:
                            print("Regional Branch User Mapping already exists")
                            utils.script_stats["regional_mapping_already_exists"] += 1

    except Exception as err:
        print(err)
        traceback.print_exc()

# Call the script
MappingScript()



print("\n\n\n")
print("===== script_stats =====")
print(utils.script_stats)
print("\n\n\n")



"""
python3 manage.py shell
exec(open('excel_script/2023_12_11/upload_data_2023_12_11.py').read())
"""