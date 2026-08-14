from rest_framework import serializers
from .models import TeleVerification , Videokyc

class tele_verificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeleVerification
        fields="__all__"

class VideokycSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videokyc
        fields = "__all__"