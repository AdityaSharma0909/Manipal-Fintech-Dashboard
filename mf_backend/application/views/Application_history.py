from rest_framework.views import APIView
from application.models import Application
from utils.responseHandler import HttpResponse
from application.serializers import ApplicationWithHistorySerializer , ApplicationHistorySerializer

class ApplicationHistoryView(APIView):
    
    def get(self, request):
        try:
            user = request.user
            application_id = request.GET.get('application_id')

            if not application_id:
                return HttpResponse.BadRequest("Application ID Required")

            # Fetching Application object
            try:
                application = Application.objects.get(application_id=application_id)
            except Application.DoesNotExist:
                return HttpResponse.BadRequest("Application Not Found")

            # Retrieve the historical records for the found Application object
            history_records = application.history.all().order_by('-history_date')  # Sorting in descending order
            history_serializer = ApplicationHistorySerializer(history_records, many=True)
            
            # Serialize the historical records
            serializer = ApplicationWithHistorySerializer(application, context={"history" : history_serializer.data})

            # Return the serialized historical records in the response
            return HttpResponse.Success({"application": serializer.data})

        except Exception as e:
            return HttpResponse.InternalServerError(str(e))