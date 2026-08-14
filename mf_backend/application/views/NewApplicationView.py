from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from application.models import NewApplication
from application.serializers import NewApplicationSerializer
import traceback
from uuid import UUID
from django.db.models import Q
from utils.common import generate_application_number
from onboarding_v2.constants import LeadStatus
from onboarding_v2.models import ApplicationV2

class NewApplicationView(APIView):
    def _is_uuid(self, value):
        try:
            UUID(str(value))
            return True
        except (TypeError, ValueError):
            return False

    def _resolve_onboarding_application(self, application_identifier=None, lead_identifier=None):
        if application_identifier:
            filters = Q(application_id=str(application_identifier))
            if self._is_uuid(application_identifier):
                filters |= Q(id=application_identifier)
            return ApplicationV2.objects.filter(filters).first()

        if lead_identifier and self._is_uuid(lead_identifier):
            return ApplicationV2.objects.filter(lead_id=lead_identifier).order_by("-created_at").first()

        return None

    def _find_new_application(self, application_identifier):
        filters = Q(onboarding_application__application_id=str(application_identifier))
        if self._is_uuid(application_identifier):
            filters |= Q(new_application_id=application_identifier)
            filters |= Q(onboarding_application_id=application_identifier)
        return NewApplication.objects.filter(filters).first()

    def _sync_lead_status(self, application):
        lead = None
        if application.onboarding_application_id:
            lead = application.onboarding_application.lead
        elif application.account_id:
            lead = application.account.lead

        if lead and lead.status != LeadStatus.AUTO_CLOSED:
            lead.status = LeadStatus.APPLICATION_CREATED
            lead.save(update_fields=["status", "modified_at"])

    def post(self, request):
        try:
            data = request.data.copy()
            application_identifier = (
                data.get("onboarding_application")
                or data.get("application")
                or data.get("application_id")
            )
            lead_identifier = data.get("lead") or data.get("lead_id")

            for alias in ("application", "application_id", "lead", "lead_id"):
                data.pop(alias, None)

            onboarding_application = self._resolve_onboarding_application(
                application_identifier=application_identifier,
                lead_identifier=lead_identifier,
            )
            if application_identifier and not onboarding_application:
                return HttpResponse.BadRequest("Onboarding application not found")
            if lead_identifier and not application_identifier and not onboarding_application:
                return HttpResponse.BadRequest("Application not found for given lead")
            if onboarding_application:
                data["onboarding_application"] = str(onboarding_application.pk)

            loan_type = data.get("loan_type")
            if not loan_type and onboarding_application:
                loan_type = (
                    onboarding_application.lead.product_subcategory
                    or onboarding_application.loan_type
                )

            data["application_number"] = generate_application_number(loan_type)
            data["created_by"] = getattr(request.user, "pk", None)
            data["modified_by"] = getattr(request.user, "pk", None)

            serializer = NewApplicationSerializer(data=data)
            if serializer.is_valid():
                application = serializer.save()
                self._sync_lead_status(application)
                return HttpResponse.Success({"application": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    def get(self, request):
        try:
            app_id = request.GET.get("application_id")

            if app_id:
                obj = self._find_new_application(app_id)
                if not obj:
                    return HttpResponse.BadRequest("Application not found")
                return HttpResponse.Success({"application": NewApplicationSerializer(obj).data})

            all_apps = NewApplication.objects.all()
            return HttpResponse.Success({"applications": NewApplicationSerializer(all_apps, many=True).data})

        except NewApplication.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    def patch(self, request):
        try:
            app_id = request.GET.get("application_id")
            obj = self._find_new_application(app_id)
            if not obj:
                return HttpResponse.BadRequest("Application not found")

            data = request.data.copy()
            data["modified_by"] = getattr(request.user, "pk", None)

            serializer = NewApplicationSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"application": serializer.data})

            return HttpResponse.BadRequest(serializer.errors)

        except NewApplication.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    def delete(self, request):
        try:
            obj = self._find_new_application(request.GET.get("application_id"))
            if not obj:
                return HttpResponse.BadRequest("Application not found")
            obj.delete()
            return HttpResponse.Success({"msg": "Application deleted"})

        except NewApplication.DoesNotExist:
            return HttpResponse.BadRequest("Application not found")
