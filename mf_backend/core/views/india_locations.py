from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from utility.response_handler import HttpResponse
from core.service.india_location_data import (
    get_all_states_and_uts,
    find_districts_by_state,
    find_districts_by_state_code,
    get_all_states_uts_with_codes,
)


class IndiaStatesDistrictsView(APIView):
    @extend_schema(operation_id="core_india_states_districts_retrieve")
    def get(self, request, *args, **kwargs):
        state_name = request.GET.get("state") or request.GET.get("State")
        state_code = (
            request.GET.get("state_code")
            or request.GET.get("stateCode")
            or request.GET.get("StateCode")
        )

        if not state_name and not state_code:
            return HttpResponse().response(
                code=200,
                data={
                    "message": "All Indian states and union territories",
                    "count": len(get_all_states_and_uts()),
                    "states": get_all_states_and_uts(),
                    "states_with_code": get_all_states_uts_with_codes(),
                },
            )

        if state_code:
            matched = find_districts_by_state_code(state_code)
            query = state_code
        else:
            matched = find_districts_by_state(state_name)
            query = state_name

        if not matched:
            return HttpResponse().response(
                code=404,
                data=None,
                error_code=404,
                error_msg="No state/UT found for the given value.",
            )

        return HttpResponse().response(
            code=200,
            data={
                "query": query,
                "match_count": len(matched),
                "results": matched,
            },
        )


class IndiaStatesDistrictsSlashView(IndiaStatesDistrictsView):
    @extend_schema(operation_id="core_india_states_districts_slash_retrieve")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
