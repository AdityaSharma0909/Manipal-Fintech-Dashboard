from rest_framework import serializers
from .models import Branch, BranchUserMapping, StampDutyCharges
from utils.constants import ROLES
from users.models import User
import traceback
from users.serializers import UserResponseSerializer

 
class StampDutyChargesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StampDutyCharges
        fields = '__all__'


class CreateBranchSerializer(serializers.ModelSerializer):
    # stamp_duties = StampDutyChargesModelSerializer(source="branch_stamp_duty", many=True, required=False)#, read_only=True)
    
    class Meta:
        model = Branch
        fields = '__all__'

    def save(self):
        branch=Branch(**self.validated_data)
        branch.save()
        return branch


class UpdateBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    stamp_duties = StampDutyChargesModelSerializer(source="branch_stamp_duty", many=True, read_only=True)
    branch_manager=UserResponseSerializer()
    assistant_bm=UserResponseSerializer()
    cluster_manager=UserResponseSerializer()
    regional_head=UserResponseSerializer()
    loan_managers=serializers.SerializerMethodField()
    class Meta:
        model = Branch
        fields = '__all__'



    # def get_branch_manager(self,obj):
    #     try:
    #         print(obj.branch_id)
    #         branch=Branch.objects.get(branch_id=obj.branch_id)
    #         branch_manager=BranchUserMapping.objects.filter(branch=str(branch.branch_id))
    #         print(branch_manager)
    #         li=[]
    #         if branch_manager:
    #             for manager in branch_manager:
    #                 if manager.user.role==ROLES.BRANCH_MANAGER.value:
    #                     li.append(manager.user)
    #             return UserResponseSerializer(li,many=True).data
    #         else:
    #             return None
    #     except Exception as e:
    #         traceback.print_exc()
    #         return str(e)
    def get_loan_managers(self,obj):
        try:

            branch=Branch.objects.get(branch_id=obj.branch_id)
            branch_manager=BranchUserMapping.objects.filter(branch=str(branch.branch_id))

            li=[]
            if branch_manager:
                for manager in branch_manager:
                    if manager.user.role==ROLES.LOAN_OFFICER.value:
                        li.append(manager.user)
                return UserResponseSerializer(li,many=True).data
            else:
                return None
            
            
        except Exception as e:
            traceback.print_exc()
            return str(e)




class BranchUserMappingModelSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = BranchUserMapping
        fields = '__all__'