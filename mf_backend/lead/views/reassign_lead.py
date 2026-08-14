from lead.models import Lead
from branch.models import Branch , BranchUserMapping
from users.models import User
from utils.responseHandler import HttpResponse
from application.models import Application
from account.models import Account
from rest_framework.views import APIView
from geopy.distance import geodesic
from utils.constants import ACCOUNT_STATUS , APPLICATION_STATUS ,ROLES

class AssignLeadView(APIView):
    def post(self, request):
        lead_id = request.GET.get("lead_id")
        lead = Lead.objects.get(lead_id=lead_id)

        if not lead.latitude or not lead.longitude:
            return HttpResponse.BadRequest({"error": "Lead location not provided."})

        closest_branch = self.get_closest_branch(lead.latitude, lead.longitude)
        if not closest_branch:
            return HttpResponse.BadRequest({"error": "No branches found."})

        assigned_lm = self.get_least_loaded_lm(closest_branch)

        if not assigned_lm:
            return HttpResponse.BadRequest({"error": "No Loan Managers available."})

        # Assign the lead
        lead.assigned_to = assigned_lm.user
        lead.created_by = assigned_lm.user
        lead.save()

        return HttpResponse.Success({"message": "Lead assigned successfully."})

    def get_closest_branch(self, lead_latitude, lead_longitude):
        branches = Branch.objects.all()
        closest_branch = None
        min_distance = float('inf')

        for branch in branches:
            if branch.latitude and branch.longitude:
                distance = self.calculate_distance(lead_latitude, lead_longitude, branch.latitude, branch.longitude)
                if distance < min_distance:
                    min_distance = distance
                    closest_branch = branch

        return closest_branch

    def get_least_loaded_lm(self, branch):
        lm_list = BranchUserMapping.objects.filter(branch=branch, user__role=ROLES.LOAN_OFFICER.value, user__is_active=True)
        lm_with_least_load = None
        min_load = float('inf')

        for lm in lm_list:
            accounts_count = Account.objects.filter(
                created_by=lm.user
            ).exclude(status=ACCOUNT_STATUS.ACCOUNT_CONFIRMED.value).count()

            applications_count = Application.objects.filter(
                Originatedby=lm.user
            ).exclude(status=APPLICATION_STATUS.APPLICATION_INITIATED.value).count()

            total_load = accounts_count + applications_count

            if total_load < min_load:
                min_load = total_load
                lm_with_least_load = lm

        return lm_with_least_load
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # Convert latitude and longitude to tuples
        coord1 = (lat1, lon1)
        coord2 = (lat2, lon2)

        # Calculate the geodesic distance
        return geodesic(coord1, coord2).kilometers


