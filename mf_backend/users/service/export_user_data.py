from users.models import User

class ExportUserService():

    def exportUser(self, request, include_customers=False, doj_start_date=None, doj_end_date=None, creation_start_date=None, creation_end_date=None, state=None, district=None, role=None, status=None, designation=None, team=None):
        """
        Export user data to list format
        
        Args:
            request: HTTP request object
            include_customers: Boolean to include CUSTOMER role users
            
        Returns:
            List of user data rows
        """
        from django.db.models import Q

        if include_customers:
            users = User.objects.all()
        else:
            users = User.objects.all().exclude(role='CUSTOMER')

        # Apply optional date_of_joining filters
        if doj_start_date:
            users = users.filter(date_of_joining__gte=doj_start_date)
        if doj_end_date:
            users = users.filter(date_of_joining__lte=doj_end_date)
            
        # Apply optional creation filters
        if creation_start_date:
            users = users.filter(date_joined__date__gte=creation_start_date)
        if creation_end_date:
            users = users.filter(date_joined__date__lte=creation_end_date)
            
        # Apply state and district filters
        if state:
            states = [s.strip() for s in state.split(",") if s.strip()]
            if states:
                state_q = Q()
                for s in states:
                    state_q |= Q(state__icontains=s)
                users = users.filter(state_q)
                
        if district:
            districts = [d.strip() for d in district.split(",") if d.strip()]
            if districts:
                dist_q = Q()
                for d in districts:
                    dist_q |= Q(district__icontains=d)
                users = users.filter(dist_q)
                
        # Apply role, designation, team, status filters
        if role:
            roles = [r.strip() for r in role.split(",") if r.strip()]
            if roles:
                users = users.filter(role__in=roles)
                
        if designation:
            designations = [d.strip() for d in designation.split(",") if d.strip()]
            if designations:
                users = users.filter(designation__in=designations)
                
        if team:
            teams = [t.strip() for t in team.split(",") if t.strip()]
            if teams:
                users = users.filter(team__in=teams)
                
        if status:
            if status.strip().lower() == "active":
                users = users.filter(is_active=True)
            elif status.strip().lower() == "inactive":
                users = users.filter(is_active=False)
        
        userData = []

        for u in users:
            singleUserData = []
            # username, first_name, last_name
            singleUserData.append(u.username if getattr(u, 'username', None) else '-')
            singleUserData.append(u.first_name if u.first_name else '-')
            singleUserData.append(u.last_name if u.last_name else '-')

            # phone, role, designation
            singleUserData.append(str(u.phone) if u.phone else '-')
            singleUserData.append(u.role if u.role else '-')
            singleUserData.append(u.designation if getattr(u, 'designation', None) else '-')

            # aadhar, pan
            singleUserData.append(u.aadhar_no if u.aadhar_no else '-')
            singleUserData.append(u.pan_no if u.pan_no else '-')

            # employee_id, profile photo URL
            singleUserData.append(u.employee_id if getattr(u, 'employee_id', None) else '-')
            if getattr(u, 'employee_profile_photo', None):
                try:
                    photo_url = u.employee_profile_photo.url
                except Exception:
                    photo_url = str(u.employee_profile_photo)
                singleUserData.append(photo_url)
            else:
                singleUserData.append('-')

            # date_of_joining, email, entity_id, state, district
            singleUserData.append(str(u.date_of_joining) if u.date_of_joining else '-')
            singleUserData.append(u.email if u.email else '-')
            singleUserData.append(u.entity_id if getattr(u, 'entity_id', None) else '-')
            singleUserData.append(u.state if getattr(u, 'state', None) else '-')
            singleUserData.append(u.district if getattr(u, 'district', None) else '-')

            userData.append(singleUserData)
        
        return userData

