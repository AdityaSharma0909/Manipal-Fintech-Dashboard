from rest_framework.views import APIView
from account.models import Account
from users.models import User
from application.models import Application
from utils.constants import ROLES , APPLICATION_STATUS
from utils.responseHandler import HttpResponse
from django.db import transaction

class ReassignAccount(APIView):

    def post(self,request):
        """requestBody = {
            source_username: destination_username
        }"""

        user=request.user
        
        if user.role != ROLES.CPC.value:
            return HttpResponse.BadRequest({"error":"Only CPC is allowed"})
        
        
        source = request.data.keys()
        destination = request.data.values()
        sourceUsers = User.objects.filter(username__in=source, is_active=True)
        destinationUsers = User.objects.filter(username__in=destination, is_active=True)
        print("req",sourceUsers)

        updated_account = 0
        updated_application = 0

        data = {}
        with transaction.atomic():
            """
            data = {
                "00123": {
                    "source_user": {
                        ... user model
                    },
                    "destination_user": {
                        ... user model
                    }
                }
            }
             """

            #sourceUsers = ["00123",2,3,4]
            for su in sourceUsers:
                destination_username = request.data.get(su.username)
                destination_user = next((du for du in destinationUsers if du.username == destination_username), None)
                if destination_user:
                    data[su.username] = {
                        'source_user': su,
                        'destination_user': destination_user
                    }

            account = Account.objects.filter(created_by__in=sourceUsers)
            for acc in account:
                acc.created_by = data[acc.created_by.username]['destination_user']
                acc.save()
                updated_account += 1
            
            application = Application.objects.filter(Originatedby__in=sourceUsers)
            for app in application:
                app.Originatedby = data[app.Originatedby.username]['destination_user']
                print(destination_user)
                app.save()
                updated_application += 1

            for su in sourceUsers:
                su.is_active = False
                su.save()

            return HttpResponse.Success(f"Total {updated_account} account and {updated_application} application updated")


