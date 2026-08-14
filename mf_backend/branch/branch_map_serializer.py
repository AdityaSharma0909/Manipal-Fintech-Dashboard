from rest_framework import serializers

from branch.models import BranchUserMapping
from branch.serializers import UpdateBranchSerializer
from users.models import User
from dateutil import parser as parser

class BranchMappingSerializer(serializers.ModelSerializer):

    branch=UpdateBranchSerializer(many=False)
    class Meta:
        model=BranchUserMapping
        fields='__all__'


class UpdateBranchMapping(serializers.ModelSerializer):
    class Meta:
        model = BranchUserMapping
        fields = '__all__'

class UserEmployeeResponseSerializer(serializers.ModelSerializer):

    branch=BranchMappingSerializer(many=True,source='lm_branch_map.all')
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ['aadhar_no']
        extra_kwargs={
            'password':{'write_only':True},
            'groups': {'write_only': True},
            'user_permissions': {'write_only': True}

        }
    def to_representation(self, instance):
        representation=super().to_representation(instance)
        if representation['date_of_joining'] is not None:
            representation['date_of_joining']=parser.parse(representation['date_of_joining'])

        if representation['branch']:
            representation['branch']=representation['branch'][0]
        
        # Add assigned_to key with the same value as assign_so
        representation['assigned_to'] = representation.get('assign_so')
        
        return representation