from rest_framework import serializers

from users.serializers import UserResponseSerializer
from .models import Disbursement 

class DisbursementSerializer(serializers.ModelSerializer):
    #created_by = UserResponseSerializer()
    class Meta:
        model = Disbursement
        fields="__all__"