from utility.common_utils import custom_response_obj
from utility.crud_helper import CrudHelper


class BranchService(CrudHelper):

    def get_all_branches(self):
        data=self.get_all_data().get('data')
        keys_with_branch_name={branch.get('branch_name'):branch for branch in data}
        keys_with_branch_code = {branch.get('branch_code'): branch for branch in data }
        return custom_response_obj(message={'branch_names':keys_with_branch_name,
                                            'branch_codes':keys_with_branch_code},
                                   code=200)