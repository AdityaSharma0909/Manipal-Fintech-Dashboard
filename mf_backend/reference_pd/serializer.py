from rest_framework import serializers

from .models import Reference_PD 

class Reference_PDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference_PD
        fields="__all__"