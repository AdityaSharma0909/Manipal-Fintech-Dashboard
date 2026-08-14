from typing import Optional
from apps.data.repositories.base_repository import BaseRepository
from apps.models.lead_model import CustomerCrmLead


class LeadRepository(BaseRepository[CustomerCrmLead]):
    """
    Repository for managing Customer CRM Leads.
    """
    model = CustomerCrmLead

    def get_by_mobile(self, mobile_number: str) -> Optional[CustomerCrmLead]:
        """
        Fetch the most recent lead by mobile number.
        """
        return self.get_queryset().filter(mobile_number=mobile_number).order_by("-created_at").first()

    def update_lead_number(self, lead_id: str, lead_number: str) -> bool:
        """
        Update the ICICI generated lead number for a specific lead record.
        """
        lead = self.get_by_id(lead_id)
        if lead:
            self.update(lead, icici_lead_number=lead_number)
            return True
        return False
