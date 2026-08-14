from rest_framework.views import APIView
from utils.responseHandler import HttpResponse 
from disbursements.models import Disbursement

class DisbursementUpdateView(APIView):
    def patch(self, request):
        try:
            disbursements_data = request.data.get('disbursements', [])

            updated_disbursements = []

            for disbursement_data in disbursements_data:
                disbursement_id = disbursement_data.get('disbursement_id')
                utr_number = disbursement_data.get('utr_no')
                modified_at = disbursement_data.get('modified_at')

                disbursement = Disbursement.objects.get(disbursement_id=disbursement_id)

                
                disbursement.utr_no = utr_number
                disbursement.modified_at = modified_at
                disbursement.save()

                updated_disbursements.append(disbursement_data)

            return HttpResponse.Success(updated_disbursements)
        
        except Disbursement.DoesNotExist:
            return HttpResponse.BadRequest("Disbursement not found")
        
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
