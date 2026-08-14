from lead.serializers import LeadDisplaySerializer
from utility.crud_helper import CrudHelper


class LeadService:

    lead_instance=CrudHelper(LeadDisplaySerializer)


    def delete_obj(self, lead_id):
        return self.lead_instance.delete_obj(lead_id)