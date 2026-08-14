from rest_framework.views import APIView
from loan.models import Loan
from utils.responseHandler import HttpResponse

class LoanHistoryView(APIView):
    def get(self, request, *args, **kwargs):
        loan = Loan.objects.get(loan_id=request.GET.get("loan_id", ""))
        history = loan.history.all()

        history_data = []
        for record in history:
            history_data.append({
                'date': record.history_date.strftime('%Y-%m-%d %H:%M:%S'),
                'user': record.history_user.username,
                'changes': record.history_change_reason,
                'type':record.history_type
            })

        return HttpResponse.Success({'history_data': history_data})