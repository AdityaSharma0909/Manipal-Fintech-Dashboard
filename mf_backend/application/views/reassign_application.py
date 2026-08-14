from rest_framework.views import APIView
from users.models import User
from application.models import Application
from utils.constants import ROLES , APPLICATION_STATUS
from utils.responseHandler import HttpResponse
from django.db import transaction

class ReassignApplication(APIView):

    def post(self, request):
        user = request.user
        
        if user.role != ROLES.CPC.value:
            return HttpResponse.BadRequest({"error": "Only CPC is allowed"})
        
        application_id = request.GET.get('application_id', "")
        if not application_id:
            return HttpResponse.BadRequest({"error": "application_id is required"})
        
        try:
            application = Application.objects.get(application_id=application_id)
        except Application.DoesNotExist:
            return HttpResponse.BadRequest({"error": "Application not found"})

        assign_to = request.data.get("assign_to")
        if not assign_to:
            return HttpResponse.BadRequest({"error": "assign_to is required"})
        print(assign_to)
        # Assuming assign_to is the ID of a user, fetch the user object
        try:
            assign_to_user = User.objects.get(username=assign_to , is_active=True)
            print(assign_to_user)
        except User.DoesNotExist:
            return HttpResponse.BadRequest({"error": "Assigned user not found"})

        with transaction.atomic():
            application.Originatedby = assign_to_user
            application.save()

        return HttpResponse.Success("Application updated")