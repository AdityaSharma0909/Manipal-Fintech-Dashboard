from rest_framework import serializers

from loan.models import DemandGeneration


class BillGenerationSerializer(serializers.ModelSerializer):

    class Meta:
        model=DemandGeneration
        fields='__all__'