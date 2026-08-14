from rest_framework.views import APIView

from branch.serializers import CreateBranchSerializer
from branch.services.branches_service import BranchService
from utility.api_framework import ApiFramework


class AllBranches(ApiFramework):

    def __init__(self):
        super().__init__()

    def process(self):
        service=BranchService(CreateBranchSerializer).get_all_branches()
        return service


class AllBranchesView(APIView):

    def get(self, request):
        return AllBranches().main()