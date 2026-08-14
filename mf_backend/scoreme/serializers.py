from rest_framework import serializers
from scoreme.models import ScoreMeBankAnalysis

class ScoreMeBankAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreMeBankAnalysis
        exclude = ['webhook_response']