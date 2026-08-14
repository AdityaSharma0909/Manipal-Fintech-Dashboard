
from rest_framework.views import APIView
from openpyxl import load_workbook
from cibil_score.models import CibilScore
from application.models import Application
from cibil_score.serializer import CibilScoreSerializer
from utils.responseHandler import HttpResponse

class UploadCibilScoreView(APIView):
    def post(self, request):
        user = request.user
        application_id = request.GET.get('application_id')
        excel_file = request.FILES.get('excel_file')

        if not application_id or not excel_file:
            return HttpResponse.BadRequest({'error': 'Please provide both application_id and excel_file'})

        try:
            application = Application.objects.get(application_id=application_id)
        except Application.DoesNotExist:
            return HttpResponse.BadRequest({'error': 'Application not found'})

        wb = load_workbook(excel_file)
        sheet = wb.active

        obligation = sheet['C15'].value
        existing_loan_amount = sheet['C18'].value
        emi_of_existing_loan = sheet['C19'].value
        no_of_loans_running = sheet['C45'].value
        no_of_loans_closed_in_last_1_year = sheet['C46'].value
        any_loan_applied_in_last_30_days = sheet['C47'].value

        if any_loan_applied_in_last_30_days is not None and str(any_loan_applied_in_last_30_days).lower() == 'yes':
            any_loan_applied_in_last_30_days = 'YES'
        else:
            any_loan_applied_in_last_30_days = 'NO'

        cibil_score_data = {
            'application': application.application_id,
            'obligation': obligation,
            'existing_loan_amount': existing_loan_amount,
            'emi_of_existing_loan': emi_of_existing_loan,
            'no_of_loans_running': no_of_loans_running,
            'no_of_loans_closed_in_last_1_year': no_of_loans_closed_in_last_1_year,
            'any_loan_applied_in_last_30_days': 'YES' if any_loan_applied_in_last_30_days else 'NO',
            "created_by": user.user_id
        }

        # Check if credit score already exists for this application
        existing_cibil_score = CibilScore.objects.filter(application=application).first()

        if existing_cibil_score:
            # Update existing credit score
            serializer = CibilScoreSerializer(existing_cibil_score, data=cibil_score_data)
        else:
            # Create new credit score
            serializer = CibilScoreSerializer(data=cibil_score_data)

        if serializer.is_valid():
            serializer.save()
            return HttpResponse.Success({'cibil_score': serializer.data})
        else:
            return HttpResponse.BadRequest(serializer.errors)