from decimal import Decimal, InvalidOperation

from django.db.models import Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.views import APIView

from onboarding_v2.models import ProductV2
from onboarding_v2.serializers.product import ProductV2Serializer
from utils.responseHandler import HttpResponse


class ProductV2ListView(APIView):
    @extend_schema(
        tags=["Onboarding V2"],
        summary="List eligible onboarding products",
        parameters=[
            OpenApiParameter("available_for", OpenApiTypes.STR),
            OpenApiParameter("category", OpenApiTypes.STR),
            OpenApiParameter("repayment_frequency", OpenApiTypes.STR),
            OpenApiParameter("tenure_months", OpenApiTypes.INT),
            OpenApiParameter("required_amount", OpenApiTypes.NUMBER),
        ],
        responses={200: ProductV2Serializer(many=True)},
    )
    def get(self, request):
        qs = ProductV2.objects.filter(is_active=True)

        available_for = request.query_params.get("available_for")
        if available_for:
            qs = qs.filter(available_for__contains=[available_for.strip()])

        category = request.query_params.get("category")
        if category:
            category = category.strip()
            category_aliases = {
                "GENERAL_PURPOSE": "general purpose",
                "AGRI_ALLIED": "agri",
                "MSME": "msme",
                "CONSUMPTION_LOAN": "consumption",
                "INCOME_LOAN": "income",
            }
            alias = category_aliases.get(category.upper())
            category_query = Q(category__iexact=category)
            if alias:
                category_query |= Q(category__icontains=alias)
            qs = qs.filter(category_query)

        repayment_frequency = request.query_params.get("repayment_frequency")
        if repayment_frequency:
            qs = qs.filter(
                repayment_frequency__iexact=repayment_frequency.strip()
            )

        tenure_months = request.query_params.get("tenure_months")
        if tenure_months:
            try:
                qs = qs.filter(tenure_months=int(tenure_months))
            except (TypeError, ValueError):
                return HttpResponse.BadRequest("tenure_months must be an integer.")

        required_amount = request.query_params.get("required_amount")
        if required_amount:
            try:
                amount = Decimal(required_amount)
            except (InvalidOperation, TypeError, ValueError):
                return HttpResponse.BadRequest("required_amount must be numeric.")
            qs = qs.filter(
                minimum_ticket_size__lte=amount,
                maximum_ticket_size__gte=amount,
            )

        serializer = ProductV2Serializer(qs, many=True)
        return HttpResponse.Success(
            {"count": qs.count(), "results": serializer.data}
        )
