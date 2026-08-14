from lead.models import Lead

class ExportLeadService():

    def get_lead_data(self,query_options={}):
        query_options_available = ['lead_id__in', 'created_at__gte', 'created_at__lte', 'lead_type', 'address_line',
        'pincode', 'city' , 'state', 'country', 'phone',
        'status']
        
        filter_query = {}
        if len(query_options)>0:
            for i in query_options_available:
                opt = query_options.get(i)
                if opt is not None:
                    if i =='lead_id__in':
                        opt=opt.split(",")
                        filter_query[i] = opt
        
        leads = Lead.objects.filter(**filter_query).prefetch_related(
            
        )

        leadData = []

        for lead in leads:

            single_lead_data=[
                lead.first_name,
                lead.last_name,
                lead.lead_type,
                lead.address_line,
                lead.pincode,
                lead.city,
                lead.state,
                lead.country,
                lead.phone,
                lead.status,
                lead.assigned_to if lead.assigned_to else None,
                lead.assigned_to.username if lead.assigned_to else None,
                lead.lending_type,
                lead.created_at.strftime('%d/%m/%Y, %H:%M'),
            ]

            leadData.append(single_lead_data)

        return leadData