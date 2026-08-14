from rest_framework.views import APIView
from application.models import Application
from utils.responseHandler import HttpResponse

class ApplicationHistoryView(APIView):
    def get(self, request, *args, **kwargs):
        application = Application.objects.get(application_id=request.GET.get("application_id", ""))
        history = application.history.all()

        history_data = []
        for record in history:
            history_data.append({
                'date': record.history_date.strftime('%Y-%m-%d %H:%M:%S'),
                'user': record.history_user.username,
                'changes': record.history_change_reason,
                'type':record.history_type
            })

        return HttpResponse.Success({'history_data': history_data})