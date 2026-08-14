import traceback

from rest_framework.views import APIView
from ..serializers import (
    BranchSerializer,
    CreateBranchSerializer,
    UpdateBranchSerializer,
    StampDutyChargesModelSerializer,
)
from utils.responseHandler import HttpResponse
from utils.constants import ROLES
from ..models import Branch, BranchUserMapping, StampDutyCharges
from users.models import User
from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework.pagination import PageNumberPagination


class BranchDetailsView(APIView, PageNumberPagination):
    def get(self, request, *args, **kwargs):
        try:
            if request.GET.get("branch_id"):
                branch = Branch.objects.get(branch_id=request.GET.get("branch_id"))
                ser = BranchSerializer(branch)
                return HttpResponse.Success({"branch": ser.data})

            return HttpResponse.BadRequest("branch_id is required")

        except Exception as e:
            return HttpResponse.InternalServerError(str(e))


class BranchView(APIView, PageNumberPagination):
    def get(self, request, *args, **kwargs):
        try:
            if request.user.role in [ROLES.CPC.value, ROLES.BUSINESS_HEAD.value]:
                # branchs=Branch.objects.all() #this exists in existing code
                branch = Branch.objects.all()
                # ser=BranchSerializer(branchs,many=True) #this exists in existing code
            else:
                branchUserMappings = BranchUserMapping.objects.filter(user=request.user)
                # branches = [] //this exists in existing code
                branch = []
                for branchUserMapping in branchUserMappings:
                    # branches.append(branchUserMapping.branch) #this exists in existing code
                    branch.append(branchUserMapping.branch)
                # ser=BranchSerializer(branches,many=True) #this exists in existing code
            # pagination changes start
            paginated_data = self.paginate_queryset(branch, request)
            resp = BranchSerializer(paginated_data, many=True).data
            resp = self.get_paginated_response(resp).data
            resp["Branch"] = resp.pop("results")
            return HttpResponse.Success(resp)
            # pagination changes end
            # return HttpResponse.Success({"branch":ser.data}) #this exists in existing code

        except Exception as e:
            return HttpResponse.InternalServerError(str(e))

    def post(self, request):
        try:

            user = request.user
            if user.role != ROLES.CPC.value:
                return HttpResponse.BadRequest({"error": "Only CPC is allowed "})

            data = request.data
            stamp_duties=data.get('stamp_duties', None)
            if not stamp_duties:
                return HttpResponse.BadRequest({'error':'Stamp duty is required'})
            if not data:
                return HttpResponse.BadRequest({"error": "Empty Data"})
            assign_user_role = User.objects.get(user_id=str(data["branch_manager"]))
            if assign_user_role.role != "BRANCH_MANAGER":
                return HttpResponse.BadRequest(
                    {"error": "Selected user role must be branch manager"}
                )

            # already_manager=Branch.objects.filter(branch_manager__user_id=str(data["branch_manager"])).first()
            # if already_manager is not None:
            #     return HttpResponse.BadRequest({"error":"Cannot assign two branch for single manager"})
            # data["branch_manager"]=User.objects.get(user_id=str(data["branch_manager"]))

            with transaction.atomic():
                ser = CreateBranchSerializer(data=data)

                if not ser.is_valid():
                    return HttpResponse.BadRequest({"error": ser.errors})

                branch = ser.save()
                if branch.branch_manager:
                    self.__branch_mapping_users(branch, branch.branch_manager)
                if branch.assistant_bm:
                    self.__branch_mapping_users(branch, branch.assistant_bm)
                if branch.regional_head:
                    self.__branch_mapping_users(branch, branch.regional_head)
                if branch.cluster_manager:
                    self.__branch_mapping_users(branch, branch.cluster_manager)

                success, stamp_duties_data = self.__stamp_duty_create_update(
                    branch=branch, stamp_duties_payload=data["stamp_duties"]
                )
                if not success:
                    return HttpResponse.BadRequest({"error": stamp_duties_data})

                resp_data = ser.data.copy()
                resp_data["stamp_duties"] = stamp_duties_data

                # return HttpResponse.Success({"message": ser.data})
                return HttpResponse.Success({"message": resp_data})
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def patch(self, request):
        user = request.user
        if user.role == ROLES.CPC.value:
            data = request.data
            prev_branch = Branch.objects.get(
                branch_id=request.GET.get("branch_id", None)
            )
            prev_branch_manager = str(prev_branch.branch_manager.user_id)
            ser = UpdateBranchSerializer(instance=prev_branch, data=data, partial=True)
            if ser.is_valid():

                print(prev_branch_manager, data.get("branch_manager"))
                if prev_branch_manager != data.get(
                    "branch_manager", prev_branch_manager
                ):
                    assign_user_role = User.objects.get(
                        user_id=str(data["branch_manager"])
                    )
                    if assign_user_role.role != "BRANCH_MANAGER":
                        return HttpResponse.BadRequest(
                            {"error": "Selected user role must be branch manager"}
                        )

                    branch = ser.save()
                    self.__branch_mapping_users(branch, branch.branch_manager)
                    if branch.assistant_bm != prev_branch.assistant_bm:
                        self.__branch_mapping_users(branch, branch.assistant_bm)
                    if branch.regional_head != prev_branch.regional_head:
                        self.__branch_mapping_users(branch, branch.regional_head)
                    if branch.cluster_manager != prev_branch.cluster_manager:
                        self.__branch_mapping_users(branch, branch.cluster_manager)
                else:
                    branch = ser.save()

                success, stamp_duties_data = self.__stamp_duty_create_update(
                    branch=branch, stamp_duties_payload=data["stamp_duties"]
                )
                if not success:
                    return HttpResponse.BadRequest({"error": stamp_duties_data})

                resp_data = ser.data.copy()
                resp_data["stamp_duties"] = stamp_duties_data

                return HttpResponse.Success({"message": resp_data})
            return HttpResponse.BadRequest({"error": ser.errors})

    def __branch_mapping_users(self, branch, user):

        BranchUserMapping.objects.create(
            branch=branch,
            user=user,
            source_id=500,
        ).save()

    def __stamp_duty_create_update(self, branch, stamp_duties_payload):
        prev_sd = StampDutyCharges.objects.filter(branch=branch)
        prev_sd.delete()

        for each_data in stamp_duties_payload:
            each_data["branch"] = str(branch.branch_id)
        sd_ser = StampDutyChargesModelSerializer(data=stamp_duties_payload, many=True)
        if not sd_ser.is_valid():
            return False, sd_ser.errors
        try:
            sd_ser.save()
        except IntegrityError as e:
            return False, str(e)
        return True, sd_ser.data

    # @action(methods=['get'],detail=False,url_path='branchDetails')
    # def get(self, request, *args, **kwargs):
    #     user = request.user
    #     if request.user.role==ROLES.CPC.value:
    #         branch=Branch.objects.get(branch_id = request.GET.get("branch_id"))
    #         ser=BranchSerializer(branch)
    #         return HttpResponse.Success({"branch":ser.data})
    #     return HttpResponse.BadRequest({"error": "Only CPC is allowed "})
