from uuid import UUID
from account.models import Account
from application.models import Application
from users.models import User
from utils.representation_serializers import Representation_modified_bySerializer,Representation_created_bySerializer,Representation_OriginatedbySerializer,Representation_AccountSerializer,Representation_ApplicationSerializer

class RepresentationUtil():
    def __init__(self, representation):
        self.representation = representation

    def change_all (self):
        if 'modified_by' in self.representation:
            modified_by = self.representation['modified_by']
            if modified_by and type(modified_by)==UUID:
                modified_by_username = User.objects.get(user_id=modified_by)
                modified_by_ser = Representation_modified_bySerializer(modified_by_username)
                self.representation['modified_by'] = modified_by_ser.data

        if 'created_by' in self.representation:
            created_by=self.representation['created_by']
            if created_by:
                created_by_username=User.objects.get(user_id=created_by)
                created_by_ser = Representation_created_bySerializer(created_by_username)
                self.representation['created_by'] = created_by_ser.data

        if 'Originatedby' in self.representation:
            Originatedby=self.representation['Originatedby']
            if Originatedby:
                Originatedby_username=User.objects.get(user_id=Originatedby)
                Originatedby_ser = Representation_OriginatedbySerializer(Originatedby_username)
                self.representation['Originatedby'] = Originatedby_ser.data

        if 'account' in self.representation:
            account = self.representation['account']
            if account and type(account)==UUID:
                account_name = Account.objects.get(account_id=account)
                account_ser = Representation_AccountSerializer(account_name)
                self.representation['account'] = account_ser.data

        if 'application' in self.representation:
            application = self.representation['application']
            if application and type(application)==UUID:
                application_name = Application.objects.get(application_id=application)
                application_ser = Representation_ApplicationSerializer(application_name)
                self.representation['application'] = application_ser.data

        return self.representation