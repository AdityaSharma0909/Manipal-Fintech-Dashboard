# flow/coverfox.py
from rest_framework.views import APIView
from utils.responseHandler import HttpResponse
from .models import Flow
from .serializers import FlowSerializer
import traceback
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


class FlowView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            user = request.user
            params = request.query_params
            query = {}
            data = []

            pg = request.GET.get("pg", None)
            page_no = 1
            offset = 0
            page_limit = 10  # pagination limit

            # Accept either ?flow_id=FL003 or legacy ?id=FL003/UUID
            flow_id_param = request.GET.get("flow_id") or request.GET.get("id")
            category = request.GET.get("category", None)
            is_active = request.GET.get("is_active", None)

            # pagination
            if pg is not None:
                try:
                    page_no = int(pg)
                    offset = (page_no - 1) * page_limit
                except ValueError:
                    return HttpResponse.BadRequest("Please send correct 'pg' param.")

            # filters
            if flow_id_param:
                # If value looks like prefixed code (e.g., FL003), filter on flow_id field
                if str(flow_id_param).upper().startswith("FL"):
                    query["flow_id"] = flow_id_param
                else:
                    # Otherwise assume it's the UUID primary key
                    query["id"] = flow_id_param
            if category:
                query["category"] = category
            if is_active is not None:
                # Convert string ("true"/"false") to boolean
                query["is_active"] = str(is_active).lower() in ["true", "1"]

            # query execution (ordered by human-friendly flow_id like FL001, FL002, ...)
            if len(query) > 0:
                data = Flow.objects.filter(Q(**query)).order_by("flow_id")[offset: offset + page_limit]
            else:
                data = Flow.objects.all().order_by("flow_id")[offset: offset + page_limit]

            serializer = FlowSerializer(data, many=True)
            return HttpResponse.Success({"flows": serializer.data})

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    def post(self, request):
        try:
            data = request.data
            user = request.user

            data["created_by"] = str(user.user_id) if user.is_authenticated else None
            data["modified_by"] = str(user.user_id) if user.is_authenticated else None

            serializer = FlowSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return HttpResponse.Success({"flow": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def patch(self, request):
        try:
            data = request.data
            flow_id = request.GET.get("flow_id", "")
            if not flow_id:
                return HttpResponse.BadRequest("flow_id is required!")

            flow = Flow.objects.get(id=flow_id)
            serializer = FlowSerializer(flow, data=data, partial=True)

            if serializer.is_valid():
                serializer.save(modified_by=request.user if request.user.is_authenticated else None)
                return HttpResponse.Success({"flow": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        
        except Flow.DoesNotExist:
            return HttpResponse.BadRequest("Flow not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def delete(self, request):
        try:
            flow_id = request.GET.get("flow_id", "")
            if not flow_id:
                return HttpResponse.BadRequest("flow_id is required!")

            flow = Flow.objects.get(id=flow_id)
            flow.delete()
            return HttpResponse.Success({"msg": "Flow deleted successfully"})
        
        except Flow.DoesNotExist:
            return HttpResponse.BadRequest("Flow not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
