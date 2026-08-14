from rest_framework.views import APIView
from application.models import Application
from ..serializer import LoanEMIHeaderSerializer,LoanEMIRecordSerializer
from utils.responseHandler import HttpResponse
from ..models import LoanEMISchedule,LoanEMIRecord
from utils.constants import APPLICATION_STATUS

class LoanEMIView(APIView):

    def get(self, request, *args, **kwargs):
        user = request.user
        application=Application.objects.get(application_id=request.GET.get('application_id', ""))
        if application.status==APPLICATION_STATUS.LOAN_DISBURSED.value:
            # loan=Loan.objects.get(application=application)
            loan_emi_header=LoanEMISchedule.objects.filter(application=application).first()
            if loan_emi_header:
                ser=LoanEMIHeaderSerializer(loan_emi_header)
                return HttpResponse.Success({"Loan_emi_header": ser.data})
            return HttpResponse.BadRequest("error" ,"Loan_emi_header not found")
        else:
            return HttpResponse.BadRequest("error" ,"Loan_emi_header not found")

class LoanEMIRecordView(APIView):

    def get(self,request,*args,**kwargs):
        user = request.user
        if request.GET.get('emi_header_id', ""):
            loan_emi_record=LoanEMIRecord.objects.filter(loan_emi_header=request.GET.get('emi_header_id', ""))
            if loan_emi_record:
                ser=LoanEMIRecordSerializer(loan_emi_record,many=True)
            return HttpResponse.Success({"Loan_emi_record": ser.data})
        return HttpResponse.BadRequest("error" ,"Loan_emi_record not found")
        
        
       
        
        
    
   