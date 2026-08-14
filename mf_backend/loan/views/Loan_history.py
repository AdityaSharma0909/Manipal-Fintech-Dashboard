from rest_framework.views import APIView
from loan.models import Loan
from utils.responseHandler import HttpResponse
from loan.serializer import LoanHistorySerializer , LoanWithHistorySerializer

class LoanHistoryView(APIView):
    
    def get(self, request):
        try:
            user = request.user
            loan_id = request.GET.get('loan_id')

            if not loan_id:
                return HttpResponse.BadRequest("Loan ID Required")

            # Fetching Loan object
            try:
                loan = Loan.objects.get(loan_id=loan_id)
            except Loan.DoesNotExist:
                return HttpResponse.BadRequest("Loan Not Found")

            # Retrieve the historical records for the found Loan object
            history_records = loan.history.all().order_by('-history_date')  # Sorting in descending order
            history_serializer = LoanHistorySerializer(history_records, many=True)
            
            # Serialize the historical records
            serializer = LoanWithHistorySerializer(loan, context={"history" : history_serializer.data})

            # Return the serialized historical records in the response
            return HttpResponse.Success({"loan": serializer.data})

        except Exception as e:
            return HttpResponse.InternalServerError(str(e))