from rest_framework.views import APIView
from account.models import Account
from utils.responseHandler import HttpResponse
from account.serializers import AccountHistorySerializer , AccountWithHistorySerializer

class AccountHistoryView(APIView):
    
    def get(self, request):
        try:
            user = request.user
            account_id = request.GET.get('account_id')

            if not account_id:
                return HttpResponse.BadRequest("Account ID Required")

            # Fetching Account object
            try:
                account = Account.objects.get(account_id=account_id)
            except Account.DoesNotExist:
                return HttpResponse.BadRequest("Account Not Found")

            # Retrieve the historical records for the found Account object
            history_records = account.history.all().order_by('-history_date')  # Sorting in descending order
            history_serializer = AccountHistorySerializer(history_records, many=True)
            
            # Serialize the historical records
            serializer = AccountWithHistorySerializer(account, context={"history" : history_serializer.data})

            # Return the serialized historical records in the response
            return HttpResponse.Success({"account": serializer.data})

        except Exception as e:
            return HttpResponse.InternalServerError(str(e))