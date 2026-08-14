from rest_framework import serializers

from loan.models import LoanEMISchedule, LoanEMIRecord


class LoanEmiScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = LoanEMISchedule

class LoanEmiRecordSerializer(serializers.ModelSerializer):


    class Meta:
        fields = '__all__'
        model = LoanEMIRecord
