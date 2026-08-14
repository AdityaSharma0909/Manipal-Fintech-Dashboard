from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
import traceback
from django.core.exceptions import ObjectDoesNotExist
from account.models import NewAccount , NewAccountDocument
from account.serializers import NewAccountSerializer
from utils.common import generate_customer_id
from utils.constants import LEAD_DOCUMENT_TYPE
from tasks.utils import to_bool
from onboarding_v2.constants import LeadStatus

class NewAccountView(APIView):

    def post(self, request):
        try:
            user = request.user
            data = request.data.copy()  # important for mutation

            pan = data.get("pan_card_number")
            phone = data.get("phone")
            is_pan_verified = data.get("is_pan_verified", False)

            if not pan or not phone:
                return HttpResponse.BadRequest("PAN number and phone number are required")

            # 1️⃣ Check if PAN already exists
            pan_exists = NewAccount.objects.filter(pan_card_number=pan).first()
            if pan_exists:
                return HttpResponse.BadRequest("This PAN already exists in the system")

            # 2️⃣ Check if phone already exists with another PAN
            phone_exists = NewAccount.objects.filter(phone=phone).first()
            if phone_exists and phone_exists.pan_card_number != pan:
                return HttpResponse.BadRequest(
                    "This phone number is already linked with another PAN. Please use another phone number."
                )

            # 3️⃣ Generate customer_id ONLY if PAN is verified
            if to_bool(is_pan_verified):
                data["customer_id"] = generate_customer_id()   # keep blank until later verification
            else :
                return HttpResponse.BadRequest("PAN verification is required to create an account.")
            serializer = NewAccountSerializer(data=data)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            new_account = serializer.save()

            # 4️⃣ Upload PAN file after account creation
            uploaded_file = request.FILES.get("pan_card")
            if uploaded_file:
                NewAccountDocument.objects.create(
                    document_type=LEAD_DOCUMENT_TYPE.PAN_CARD.value,
                    file=uploaded_file,
                    file_name=uploaded_file.name,
                    new_account=new_account,
                    uploaded_by=user,
                )

            lead = new_account.lead
            if lead:
                lead.status = LeadStatus.APPLICATION_CREATED
                lead.save(update_fields=["status", "modified_at"])
            return HttpResponse.Success({"account": serializer.data})

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    def get(self, request):
        try:
            account_id = request.GET.get("account_id")

            if account_id:
                acc = NewAccount.objects.get(new_account_id=account_id)
                return HttpResponse.Success({"account": NewAccountSerializer(acc).data})

            accs = NewAccount.objects.all()
            return HttpResponse.Success({"accounts": NewAccountSerializer(accs, many=True).data})

        except NewAccount.DoesNotExist:
            return HttpResponse.BadRequest("Account not found")

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    def patch(self, request):
        try:
            account_id = request.GET.get("account_id")
            acc = NewAccount.objects.get(new_account_id=account_id)

            serializer = NewAccountSerializer(acc, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"account": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)

        except NewAccount.DoesNotExist:
            return HttpResponse.BadRequest("Account not found")

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    def delete(self, request):
        try:
            NewAccount.objects.get(new_account_id=request.GET.get("account_id")).delete()
            return HttpResponse.Success({"msg": "Account deleted"})

        except NewAccount.DoesNotExist:
            return HttpResponse.BadRequest("Account not found")
