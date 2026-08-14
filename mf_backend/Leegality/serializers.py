# serializers.py
from rest_framework import serializers
from .models import LeegalityDocument, Invitee

class InviteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitee
        fields = "__all__"


class LeegalityDocumentSerializer(serializers.ModelSerializer):
    invitees = InviteeSerializer(many=True, read_only=True)

    class Meta:
        model = LeegalityDocument
        fields = "__all__"
