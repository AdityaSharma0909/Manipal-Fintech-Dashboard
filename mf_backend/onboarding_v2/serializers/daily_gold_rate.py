from rest_framework import serializers

from onboarding_v2.models import DailyGoldRate, HistoricalDailyGoldRate


class DailyGoldRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyGoldRate
        fields = "__all__"


class HistoricalDailyGoldRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalDailyGoldRate
        fields = "__all__"

