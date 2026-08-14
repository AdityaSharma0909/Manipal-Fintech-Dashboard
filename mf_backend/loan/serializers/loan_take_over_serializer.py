from rest_framework import serializers

from lender.serializers import LenderSerializer
from loan.models import LoanTakeOver, TakeOverResidenceAddress, GprsPhotos
from loan.serializer import GPRSDocSerializer


class LoanTakeOverSerializer(serializers.ModelSerializer):

    class Meta:
        model=LoanTakeOver
        fields='__all__'


class LoanTakeOverDetails(serializers.ModelSerializer):
    lender=LenderSerializer()
    class Meta:
        model=LoanTakeOver
        fields='__all__'


class TakeOverResidenceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model=TakeOverResidenceAddress
        fields='__all__'


    def to_representation(self, instance):
        representation=super().to_representation(instance)
        gprs_photos=GprsPhotos.objects.filter(take_over_residence__take_over_residence_details_id=representation['take_over_residence_details_id'])
        representation['inspection_doc']=GPRSDocSerializer(gprs_photos, many=True).data
        return representation
