from rest_framework import serializers
from account.models import Account
from application.models import Application
from users.models import User

class Representation_modified_bySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username']
        
class Representation_created_bySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username']

class Representation_OriginatedbySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'username']

class Representation_AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['account_id', 'customer_id']

class Representation_ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['application_id', 'application_number']