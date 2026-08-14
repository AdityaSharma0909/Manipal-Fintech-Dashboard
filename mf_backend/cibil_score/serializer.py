from rest_framework import serializers
from cibil_score.models import CibilScore

class CibilScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CibilScore
        fields = '__all__'
