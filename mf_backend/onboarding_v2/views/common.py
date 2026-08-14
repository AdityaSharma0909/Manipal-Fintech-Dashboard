from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView

from utils.responseHandler import HttpResponse


class OnboardingHealthView(APIView):
    def get(self, request):
        return HttpResponse.Success({"status": "ok"})


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
