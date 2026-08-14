from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F
from django.utils import timezone

from application.models import Application
from branch.branch_map_serializer import UserEmployeeResponseSerializer, UpdateBranchMapping
from branch.models import BranchUserMapping
from users.models import User
from users.serializers import UserResponseSerializer, UserUpdateSerializer
from utility.common_utils import custom_response_obj
from utils import helper
from utils.constants import ROLES, ROLE_MANAGEMENT_SCOPE, API_IMMUTABLE_ROLES, DESIGNATION, TEAM

from utils.responseHandler import HttpResponse

from datetime import datetime , timedelta

from utils.common import int2base
from time import time

import logging
import re
import os
import uuid

import pandas as pd
from utils.envSetup import environment

log = logging.getLogger('radian')

class UserService:
    SHORT_ROLE_ALIASES = {
        'RH': ROLES.REGIONAL_HEAD.value,
        'BM': ROLES.BRANCH_MANAGER.value,
        'LO': ROLES.LOAN_OFFICER.value,
        'SO': ROLES.SALES_OFFICER.value,
        'CH': ROLES.CLUSTER_HEAD.value,
        'ZH': ROLES.ZONAL_HEAD.value,
        'NSH': ROLES.NATIONAL_SALES_HEAD.value,
    }

    SALES_OFFICER_BULK_COLUMN_ALIASES = {
        'ecode': ('ecode', 'employeeid', 'employee_id'),
        'name': ('name', 'fullname', 'full_name'),
        'first_name': ('firstname', 'first_name'),
        'last_name': ('lastname', 'last_name'),
        'state': ('state',),
        'district': ('district',),
        'location': ('location', 'city'),
        'mobileno': ('mobileno', 'mobile', 'mobilenumber', 'mobile_number'),
        'pincode': ('pincode', 'pin', 'pin_code'),
    }

    SALES_OFFICER_BULK_REQUIRED_COLUMNS = {
        'ecode': 'Ecode/EMPLOYEE_ID',
        'state': 'State',
        'district': 'District',
        'mobileno': 'Mobile no',
        'pincode': 'Pin Code',
    }

    def normalize_role(self, role):
        if role is None:
            return None
        token = str(role).strip().upper()
        
        # 1. Check if it's already a valid value
        if any(token == r.value for r in ROLES):
            return token
            
        # 2. Check SHORT_ROLE_ALIASES
        if token in self.SHORT_ROLE_ALIASES:
            return self.SHORT_ROLE_ALIASES[token]
            
        # 3. Check enum member names (e.g., "CPC" -> "CENTRALISED_PROCESSING_CELL")
        try:
            return ROLES[token].value
        except KeyError:
            pass
            
        return token

    def normalize_filter_token(self, value):
        return re.sub(r'[\s-]+', '_', str(value or '').strip().upper())

    def unique_values(self, values):
        unique = []
        for value in values:
            if value and value not in unique:
                unique.append(value)
        return unique

    def split_filter_values(self, values):
        if not isinstance(values, (list, tuple)):
            values = [values]

        parsed_values = []
        for value in values:
            for item in str(value or '').split(','):
                item = item.strip()
                if item:
                    parsed_values.append(item)
        return parsed_values

    def resolve_role_filter_values(self, values):
        role_aliases = {role.name: role.value for role in ROLES}
        role_aliases.update({role.value: role.value for role in ROLES})
        role_aliases.update(self.SHORT_ROLE_ALIASES)

        designation_aliases = {designation.name: designation.value for designation in DESIGNATION}
        designation_aliases.update({designation.value: designation.value for designation in DESIGNATION})

        role_values = []
        designation_values = []

        for value in self.split_filter_values(values):
            token = self.normalize_filter_token(value)
            if token in role_aliases:
                role_values.append(role_aliases[token])
            if token in designation_aliases:
                designation_values.append(designation_aliases[token])
            if token not in role_aliases and token not in designation_aliases:
                role_values.append(token)

        return self.unique_values(role_values), self.unique_values(designation_values)

    def validate_create_user_permission(self, actor_role, target_role):
        actor_role = self.normalize_role(actor_role)
        target_role = self.normalize_role(target_role)

        if not actor_role:
            return custom_response_obj(
                message={'msg': 'Unauthorized to create users'},
                code=403,
                error_msg={'msg': 'Unauthorized to create users'},
                error_code=403
            )

        if target_role in API_IMMUTABLE_ROLES:
            return self.immutable_role_response(actor_role, target_role)

        if target_role == ROLES.VERTICAL_ADMIN.value:
            return custom_response_obj(
                message={'msg': 'VERTICAL_ADMIN cannot create VERTICAL_ADMIN role user.'},
                code=403,
                error_msg={'msg': 'VERTICAL_ADMIN cannot create VERTICAL_ADMIN role user.'},
                error_code=403
            )

        if actor_role not in ROLE_MANAGEMENT_SCOPE:
            return custom_response_obj(
                message={'msg': f'{actor_role} is not authorized to create users'},
                code=403,
                error_msg={'msg': f'{actor_role} is not authorized to create users'},
                error_code=403
            )

        if target_role not in ROLE_MANAGEMENT_SCOPE.get(actor_role, ()):
            return custom_response_obj(
                message={'msg': f'{actor_role} cannot create role {target_role}'},
                code=403,
                error_msg={'msg': f'{actor_role} cannot create role {target_role}'},
                error_code=403
            )

        return None

    def normalize_bulk_column_name(self, column_name):
        if column_name is None:
            return ''
        return re.sub(r'[^a-z0-9]+', '', str(column_name).strip().lower())

    def clean_bulk_string(self, value):
        if value is None or pd.isna(value):
            return None
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return str(value).strip() or None

    def clean_bulk_numeric_string(self, value):
        cleaned = self.clean_bulk_string(value)
        if cleaned is None:
            return None
        digits = re.sub(r'[^0-9]', '', cleaned)
        return digits or None

    def split_bulk_full_name(self, full_name):
        cleaned_name = self.clean_bulk_string(full_name)
        if not cleaned_name:
            return '', ''
        parts = cleaned_name.split()
        if len(parts) == 1:
            return parts[0], ''
        return parts[0], ' '.join(parts[1:])

    def generate_bulk_upload_email(self, employee_code, used_emails=None):
        if used_emails is None:
            used_emails = set()
        base = self.sanitize_username(employee_code) or 'sales_officer'

        while True:
            suffix = uuid.uuid4().hex[:8]
            candidate = f'{base}.{suffix}@bulk-upload.local'
            if candidate in used_emails:
                continue
            if not User.objects.filter(email=candidate).exists():
                used_emails.add(candidate)
                return candidate

    def get_excel_engine_for_upload(self, file_name):
        extension = os.path.splitext(file_name or '')[1].lower()
        if extension == '.xlsx':
            return 'openpyxl'
        if extension == '.xls':
            return 'xlrd'
        return None

    def read_sales_officer_bulk_upload_file(self, excel_file):
        file_name = getattr(excel_file, 'name', '')
        extension = os.path.splitext(file_name)[1].lower()
        if extension not in ('.xlsx', '.xls'):
            raise ValueError('Only .xlsx and .xls files are supported')

        engine = self.get_excel_engine_for_upload(file_name)
        try:
            return pd.read_excel(excel_file, engine=engine)
        except ImportError as exc:
            if extension == '.xls':
                raise ValueError('Excel .xls support is unavailable because the xlrd dependency is not installed') from exc
            raise
        except Exception as exc:
            raise ValueError(f'Unable to read uploaded Excel file: {str(exc)}') from exc

    def get_sales_officer_bulk_column_map(self, dataframe_columns):
        normalized_map = {
            self.normalize_bulk_column_name(column): column
            for column in dataframe_columns
        }

        column_map = {}
        for canonical_name, aliases in self.SALES_OFFICER_BULK_COLUMN_ALIASES.items():
            for alias in aliases:
                if alias in normalized_map:
                    column_map[canonical_name] = normalized_map[alias]
                    break

        missing_headers = [
            display_name
            for normalized_name, display_name in self.SALES_OFFICER_BULK_REQUIRED_COLUMNS.items()
            if normalized_name not in column_map
        ]
        if 'name' not in column_map and 'first_name' not in column_map:
            missing_headers.append('Name or First Name')
        if missing_headers:
            raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")
        return column_map

    def build_sales_officer_bulk_row_payload(self, row, column_map, date_of_joining):
        employee_code = self.clean_bulk_string(row.get(column_map['ecode']))
        if 'name' in column_map:
            first_name, last_name = self.split_bulk_full_name(row.get(column_map['name']))
        else:
            first_name = self.clean_bulk_string(row.get(column_map['first_name'])) or ''
            last_name = self.clean_bulk_string(row.get(column_map['last_name'])) if 'last_name' in column_map else ''
            last_name = last_name or ''

        if not employee_code:
            raise ValueError('Ecode is required')

        city = self.clean_bulk_string(row.get(column_map['location'])) if 'location' in column_map else None

        return {
            'employee_id': employee_code,
            'username': employee_code,
            'first_name': first_name,
            'last_name': last_name,
            'state': self.clean_bulk_string(row.get(column_map['state'])),
            'district': self.clean_bulk_string(row.get(column_map['district'])),
            'city': city,
            'phone': self.clean_bulk_numeric_string(row.get(column_map['mobileno'])),
            'pincode': self.clean_bulk_numeric_string(row.get(column_map['pincode'])),
            'date_of_joining': date_of_joining,
            # 'email': self.generate_bulk_upload_email(employee_code, used_emails=used_emails),
            'role': ROLES.SALES_OFFICER.value,
            'designation': DESIGNATION.FOS.value,
            'team': TEAM.DST.value,
        }

    def create_sales_officers_from_excel(self, excel_file, actor_role, date_of_joining=None):
        permission_error = self.validate_create_user_permission(actor_role, ROLES.SALES_OFFICER.value)
        if permission_error:
            return permission_error

        try:
            join_date = date_of_joining or timezone.localdate()
            dataframe = self.read_sales_officer_bulk_upload_file(excel_file)
            dataframe = dataframe.dropna(how='all')
            column_map = self.get_sales_officer_bulk_column_map(dataframe.columns)

            results = []
            created_count = 0

            for index, (_, row) in enumerate(dataframe.iterrows(), start=2):
                employee_code = self.clean_bulk_string(row.get(column_map['ecode']))

                try:
                    payload = self.build_sales_officer_bulk_row_payload(
                        row=row,
                        column_map=column_map,
                        date_of_joining=join_date,
                    )
                    row_response = self.create_user(
                        data=payload,
                        actor_role=actor_role,
                        send_welcome_email=False,
                        initialize_password=False,
                    )
                except ValueError as exc:
                    row_response = custom_response_obj(
                        message={'msg': str(exc)},
                        code=400,
                        error_msg={'msg': str(exc)},
                        error_code=400
                    )

                if row_response.get('status_code') == 200:
                    created_count += 1
                    results.append({
                        'row_number': index,
                        'ecode': employee_code,
                        'status': 'created',
                        'user_id': row_response.get('data', {}).get('user_id'),
                        'error': None,
                    })
                    continue

                error_data = row_response.get('data')
                if isinstance(error_data, dict):
                    error_message = error_data.get('msg') or str(error_data)
                else:
                    error_message = str(error_data)

                results.append({
                    'row_number': index,
                    'ecode': employee_code,
                    'status': 'failed',
                    'user_id': None,
                    'error': error_message,
                })

            summary = {
                'total_rows': len(results),
                'created_count': created_count,
                'failed_count': len(results) - created_count,
                'results': results,
            }
            return custom_response_obj(message=summary, code=200)
        except ValueError as exc:
            return custom_response_obj(
                message={'msg': str(exc)},
                code=400,
                error_msg={'msg': str(exc)},
                error_code=400
            )
        except Exception as exc:
            log.exception("[BULK_UPLOAD | UserService Exception] Error - {error}".format(error=exc))
            return custom_response_obj(
                message={'msg': str(exc)},
                code=500,
                error_msg={'msg': str(exc)},
                error_code=500
            )

    def sanitize_username(self, username):
        cleaned = re.sub(r'[^A-Za-z0-9_]+', '_', (username or '').strip())
        cleaned = re.sub(r'_+', '_', cleaned).strip('_').lower()
        return cleaned[:150]

    def build_default_username(self, first_name=None, last_name=None):
        base_username = f"{first_name or ''}_{last_name or ''}"
        cleaned = self.sanitize_username(base_username)
        if cleaned:
            return cleaned
        return self.generate_username().lower()

    def build_unique_username(self, base_username):
        sanitized_base = self.sanitize_username(base_username) or self.generate_username().lower()
        if not User.objects.filter(username=sanitized_base).exists():
            return sanitized_base

        suffix = 1
        while True:
            candidate = f"{sanitized_base}_{suffix}"
            candidate = candidate[:150]
            if not User.objects.filter(username=candidate).exists():
                return candidate
            suffix += 1

    def get_immutable_role_message(self, actor_role, target_role):
        if target_role == ROLES.SUPER_ADMIN.value:
            return 'SUPER_ADMIN is the master user and can be created only once from backend.'
        if target_role == ROLES.VERTICAL_ADMIN.value:
            return f'{actor_role} cannot create VERTICAL_ADMIN role user.'
        return f'{actor_role} cannot manage {target_role} from API.'

    def immutable_role_response(self, actor_role, target_role):
        message = self.get_immutable_role_message(actor_role, target_role)
        return custom_response_obj(
            message={"msg": message},
            code=403,
            error_msg={"msg": message},
            error_code=403,
        )

    def can_manage_role(self, actor_role, target_role):
        actor_role = self.normalize_role(actor_role)
        target_role = self.normalize_role(target_role)
        if not actor_role or not target_role:
            return False
        if actor_role == ROLES.VERTICAL_ADMIN.value and target_role == ROLES.VERTICAL_ADMIN.value:
            return False
        if target_role in API_IMMUTABLE_ROLES:
            return False
        allowed_roles = ROLE_MANAGEMENT_SCOPE.get(actor_role, ())
        if actor_role == ROLES.CPC.value and target_role == ROLES.VERTICAL_ADMIN.value:
            return True
        return target_role in allowed_roles

    def generate_username(self):
        try :
            # ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 12))
            # count = User.objects.all().count()
            # start = 10000000
            # ran = int2base(start + count, 36).upper()


            epochTime = str(time()).replace('.','')
            username = int2base(int(epochTime), 36).upper()


            print("Random username: ", username)
            return username
        except Exception as e :
            raise e
    
    def createUsers(self, data, role=ROLES.CUSTOMER.value):
        print("🚫 createUsers called – NO EMAIL WILL BE SENT")

        try:
            # first_name = data.get('first_name')
            # last_name = data.get('last_name')
            # phone = str(data.get('phone'))
            # role="CUSTOMER"
            # email = data.get('email')
            # username=str(data.get('first_name')+"_"+data.get('last_name'))
            # username = "random_hex_string_of length 12 digits case insensitive"
            # data.username = username
            # data['password']= password
            # user_fields=[f.name for f in User._meta.fields]
            # new_data ={}
            # for i in data.keys():
            #     if i in user_fields:
            #         new_data[i] = data[i]
            # data.role = ROLES.CUSTOMER.value
            username = self.generate_username()
            data['username'] = username
            data['role'] = role
            user = User(**data)
            user.save()
            # User.objects.create(first_name=first_name,last_name=last_name,phone=phone, email=email,role=role,username=username).save()
            # user=User.objects.filter(phone=phone).first()
            
            return user
        except Exception as e:
            raise e

        
    def get_users(self, pagination, request, role, filters, branch=None):
        try:
            pagination = pagination()
            default_excluded_roles = [
                ROLES.CUSTOMER.value,
                ROLES.SUPER_ADMIN.value,
            ]

            if role != ROLES.LOAN_OFFICER.value:
                filter_data = {}
                role_filter_q = Q()
                role_filter_roles = []
                role_filter_designations = []
                role_filter_requested = False
                role_filter_includes_default_excluded = False
                # Collect state/district values separately for case-insensitive Q filtering
                state_values = []
                district_values = []
                if filters:
                    # Filter changes start
                    filter_options = [
                        'user_id', 'first_name', 'last_name', 'phone', 'role__in',
                        'aadhar_no', 'employee_id', 'is_active', 'email',
                        'date_of_joining', 'date_of_joining__gte', 'date_of_joining__lte',
                        'lm_branch_map__branch__branch_code', 'team', 'district__in',
                        'state', 'district', 'city', 'pincode', 'designation'
                    ]
                    
                    for i in filter_options:
                        opt = filters.get(i)
                        if opt:
                            if i == 'is_active':
                                filter_data[i] = opt[0].strip().lower() == 'true'
                            elif i == 'date_of_joining':
                                try:
                                    filter_data['date_joined__date'] = datetime.strptime(opt[0], '%Y-%m-%d').date()
                                except ValueError:
                                    pass
                            elif i in ['date_of_joining__gte', 'date_of_joining__lte']:
                                new_key = i.replace('date_of_joining', 'date_joined')
                                filter_data[new_key] = datetime.strptime(opt[0], '%Y-%m-%d') + timedelta(days=1) if i.endswith('__lte') else datetime.strptime(opt[0], '%Y-%m-%d')
                            elif i == 'role__in':
                                role_filter_roles, role_filter_designations = self.resolve_role_filter_values(opt)
                                role_filter_requested = bool(role_filter_roles or role_filter_designations)
                                role_filter_includes_default_excluded = any(
                                    role in default_excluded_roles for role in role_filter_roles
                                )
                                if role_filter_roles:
                                    role_filter_q |= Q(role__in=role_filter_roles)
                                if role_filter_designations:
                                    role_filter_q |= Q(designation__in=role_filter_designations)
                            elif i.endswith('__in'):
                                filter_values = self.split_filter_values(opt)
                                if filter_values:
                                    filter_data[i] = filter_values
                            elif i == 'state':
                                # Collect for case-insensitive filtering via Q objects
                                state_values = self.split_filter_values(opt)
                            elif i == 'district':
                                # Collect for case-insensitive filtering via Q objects
                                district_values = self.split_filter_values(opt)
                            else:
                                filter_data[i] = opt[0]
                
                if branch is None:
                    if 'branch' in filters:
                        branch_codes = filters.get('branch')
                        branch_ids = []
                        for code in branch_codes:
                            branch_ids.extend(code.split(','))
                        filter_data['lm_branch_map__branch__branch_id__in'] = branch_ids

                    # TELE_USER cannot see any users
                    if role == ROLES.TELE_USER.value:
                        return CustomResponse(
                            data=[],
                            count=0,
                            status_code=status.HTTP_200_OK,
                        )

                    # TELE_ADMIN can only see TELE_USER accounts within their own team
                    if role == ROLES.TELE_ADMIN.value:
                        filter_data.pop("role__in", None)
                        filter_data["role"] = ROLES.TELE_USER.value
                        actor_team = getattr(request.user, "team", None)
                        if actor_team:
                            filter_data["team"] = actor_team

                    print("filter_data: ", filter_data)
                    
                    user_queryset = get_user_model().objects.filter(Q(**filter_data))
                    if role_filter_requested:
                        user_queryset = user_queryset.filter(role_filter_q)

                    # Apply case-insensitive state filter
                    if state_values:
                        state_q = Q()
                        for sv in state_values:
                            state_q |= Q(state__iexact=sv)
                        user_queryset = user_queryset.filter(state_q)

                    # Apply case-insensitive district filter
                    if district_values:
                        district_q = Q()
                        for dv in district_values:
                            district_q |= Q(district__iexact=dv)
                        user_queryset = user_queryset.filter(district_q)
                    if (
                        "role" not in filter_data
                        and (
                            not role_filter_requested
                            or not role_filter_includes_default_excluded
                        )
                    ):
                        user_queryset = user_queryset.exclude(role__in=default_excluded_roles)

                    search_query = filters.get("search")
                    if search_query:
                        # Replace commas with spaces in case users type comma-separated values in search
                        search_terms = search_query[0].replace(',', ' ').split()
                        
                        combined_query = Q()
                        for term in search_terms:
                            combined_query |= (
                                Q(first_name__icontains=term) |
                                Q(last_name__icontains=term) |
                                Q(employee_id__icontains=term) |
                                Q(phone__icontains=term) |
                                Q(username__icontains=term) |
                                Q(district__icontains=term)
                            )
                        user_queryset = user_queryset.filter(combined_query)

                    # ✅ Sort by latest created (date_joined descending)
                    users = user_queryset.order_by("-date_joined")  # Latest first
                    print(f"Found {users.count()} users")
                    
                else:
                    branchMappingFilter = {}
                    for k, v in filter_data.items():
                        branchMappingFilter[f'user__{k}'] = v
                    branches = BranchUserMapping.objects.filter(
                        branch__branch_id=branch
                    ).filter(Q(**branchMappingFilter))
                    # ✅ Sort by user's date_joined
                    users = [
                        b.user for b in branches
                        if (
                            b.user.role not in default_excluded_roles
                            or role_filter_includes_default_excluded
                        )
                    ]
                    if role_filter_requested:
                        users = [
                            user for user in users
                            if (
                                user.role in role_filter_roles
                                or user.designation in role_filter_designations
                            )
                        ]
                    # Sort in Python since it's already a list
                    users = sorted(users, key=lambda u: u.date_joined, reverse=True)
                    print(branchMappingFilter)

                # Paginate and serialize
                paginated_data = pagination.paginate_queryset(users, request=request)
                serializer = UserEmployeeResponseSerializer(paginated_data, many=True)
                resp_data = pagination.get_paginated_response(serializer.data).data
                resp_data['status_code'] = 200
                resp_data['data'] = resp_data.pop('results', {})
                return resp_data
            else:
                return custom_response_obj(
                    message={'msg': 'Unauthorized to perform this operation'},
                    error_code=403,
                    error_msg={'msg': 'Unauthorized to perform this operation'},
                    code=403
                )
        except Exception as e:
            log.exception("[GET | UserService Exception] Error - {error}".format(error=e))
            return HttpResponse.InternalServerError(str(e))


    # def update_user(self, user_id, data):
    #     try:
    #         user=get_user_model().objects.get(user_id=user_id)
    #         serializer=UserUpdateSerializer(instance=user, data=data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             if 'branch_id' in data.keys():
    #                 branch_map= BranchUserMapping.objects.get(user__user_id=user_id)
    #                 branch_map_ser=UpdateBranchMapping(instance=branch_map, data={'branch':data.get('branch_id')}, partial=True)
    #                 if branch_map_ser.is_valid():
    #                     branch_map_ser.save()
    #             user = get_user_model().objects.get(user_id=user_id)
    #             return custom_response_obj(message=UserEmployeeResponseSerializer(user, many=False).data, code=200)
    #         return custom_response_obj(message=serializer.errors,
    #                                    code=400,
    #                                    error_msg=serializer.errors,
    #                                    error_code=400)

    #     except ObjectDoesNotExist:
    #         return custom_response_obj(message={'msg':f'user with user id {user_id} not found'},
    #                                    code=404,
    #                                    error_msg={'msg':f'user with user id {user_id} not found'},
    #                                    error_code=404)
    
    
    def update_user(self, user_id, data, actor_role=None):
        try:
            user = get_user_model().objects.get(user_id=user_id)

            target_role = data.get("role")
            if actor_role and target_role and target_role != user.role:
                if target_role in API_IMMUTABLE_ROLES:
                    return self.immutable_role_response(actor_role, target_role)
                if not self.can_manage_role(actor_role, target_role):
                    return custom_response_obj(
                        message={"msg": f"{actor_role} cannot assign role {target_role}"},
                        code=403,
                        error_msg={"msg": f"{actor_role} cannot assign role {target_role}"},
                        error_code=403
                    )

            # fields not allowed to edit
            restricted_fields = [
                "user_id",
                "username",
                "email",
                "employee_id",
                "phone",
                # "first_name",
                # "last_name"
            ]

            for field in restricted_fields:
                data.pop(field, None)   # safer pop

            if 'assigned_to' in data:
                data['assign_so'] = data.pop('assigned_to')

            serializer = UserUpdateSerializer(instance=user, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
                # update branch mapping if branch_id sent
                branch_id = data.get("branch_id")
                if branch_id:
                    branch_map, _ = BranchUserMapping.objects.get_or_create(user=user)
                    branch_map_ser = UpdateBranchMapping(
                        instance=branch_map,
                        data={"branch": branch_id},
                        partial=True
                    )
                    if branch_map_ser.is_valid():
                        branch_map_ser.save()
                return custom_response_obj(
                    message=UserEmployeeResponseSerializer(user).data,
                    code=200
                )
            return custom_response_obj(
                message=serializer.errors,
                code=400,
                error_msg=serializer.errors,
                error_code=400
            )

        except ObjectDoesNotExist:
            return custom_response_obj(
                message={"msg": f"user with user id {user_id} not found"},
                code=404,
                error_msg={"msg": f"user with user id {user_id} not found"},
                error_code=404
            )

        except Exception as e:
            log.exception("[PATCH | UserService Exception] Error - {error}".format(error=e))
            return HttpResponse.InternalServerError(str(e))

    def get_all_application_per_user(self, user_id, role=None):
        query = {}
        if role and role == ROLES.BRANCH_MANAGER.value:
            query['approvedByBM__user_id'] = user_id
        else:
            query['Originatedby__user_id'] = user_id
        employee_details = get_user_model().objects.get(user_id=user_id)
        apps = list(Application.objects.filter(Q(**query)).values().annotate(
            first_name=F('account__user__first_name'),
            last_name=F('account__user__last_name'),
            lm_first_name=F('Originatedby__first_name'),
            lm_last_name=F('Originatedby__last_name')
        ))
        resp = {
            'user_details': UserEmployeeResponseSerializer(employee_details, many=False).data,
            'applications': apps
        }
        return custom_response_obj(message=resp, code=200)



    def register_user(self, data, send_welcome_email=True, initialize_password=True):
        print(
            f"register_user called - send_welcome_email={send_welcome_email}, "
            f"initialize_password={initialize_password}"
        )
        to_dict = {}
        for key, value in data.items():
            if key == 'doj':
                to_dict['date_of_joining'] = value
            elif key == 'assigned_to':
                if value:
                    to_dict['assign_so_id'] = value
            elif key in ['branch_id', 'user_id']:
                continue
            else:
                to_dict[key] = value
                
        requested_username = to_dict.get('username')
        if requested_username:
            to_dict['username'] = self.sanitize_username(requested_username)
        else:
            default_username = self.build_default_username(
                first_name=to_dict.get('first_name'),
                last_name=to_dict.get('last_name'),
            )
            to_dict['username'] = self.build_unique_username(default_username)
        user = User.objects.create_user(**to_dict)
        if initialize_password:
            if getattr(environment, "MASTER_PASSWORD", None) and environment.APP_ENV == 'DEV':
                password = environment.MASTER_PASSWORD
            else:
                password = helper.generate_password()
            user.set_password(password)
            user.save()

            if send_welcome_email:
                try:
                    helper.sendEmailUser(
                        email=user.email,
                        username=user.username,
                        password=password,
                        name=f"{user.first_name} {user.last_name}"
                    )
                except Exception as e:
                    log.error(f"Failed to send password email to {user.email}: {str(e)}")
        else:
            user.set_unusable_password()
            user.save(update_fields=['password'])
        return user

    

    # for i in filter_options:
                    #     opt=filters.get(i)
                    #     if opt:
                    #         if i.endswith('__in'):
                    #             filter_data[i]=opt[0].strip().split(',')
                    #         else:
                    #             filter_data[i]=opt[0]
    

     # if 'branch' in filters:
                    #     branch_codes = filters.get('branch')
                    #     branch_codes.split(',')
                    #     filter_data['lm_branch_map__branch__branch_id__in'] = branch_codes
                    # print("filter_data: ", filter_data)
                    # users=get_user_model().objects.exclude(role=ROLES.CUSTOMER.value).filter(Q(**filter_data))
                    # print(users)

    # def create_user(self, data):
    #     try:
    #         user = User.objects.filter(phone=data.get('phone')).first()
    #         if user:
    #             return custom_response_obj(
    #                 message={'msg': 'User with this phone number already exists'}, 
    #                 code=400,
    #                 error_msg={'msg': 'User with this phone number already exists'}, 
    #                 error_code=400
    #             )
            
    #         branch_id = data.pop('branch_id', None)
    #         user = self.register_user(data)
            
    #         if branch_id:
    #             branch_map = BranchUserMapping(user=user, branch_id=branch_id)
    #             branch_map.save()
            
    #         serializer = UserEmployeeResponseSerializer(user)
    #         return custom_response_obj(message=serializer.data, code=201)
            
    #     except Exception as e:
    #         log.exception("[POST | UserService Exception] Error - {error}".format(error=e))
    #         return HttpResponse.InternalServerError(str(e))


    def create_user(self, data, actor_role=None, send_welcome_email=True, initialize_password=True):
        try:
            print("DATA RECEIVED:", data)
            actor_role = self.normalize_role(actor_role)
            target_role = self.normalize_role(data.get("role"))
            data["role"] = target_role
            if not actor_role:
                return custom_response_obj(
                    message={'msg': 'Unauthorized to create users'},
                    code=403,
                    error_msg={'msg': 'Unauthorized to create users'},
                    error_code=403
                )
            if target_role in API_IMMUTABLE_ROLES:
                return self.immutable_role_response(actor_role, target_role)
            if actor_role in ROLE_MANAGEMENT_SCOPE and target_role:
                if not self.can_manage_role(actor_role, target_role):
                    return custom_response_obj(
                        message={'msg': f'{actor_role} cannot create role {target_role}'},
                        code=403,
                        error_msg={'msg': f'{actor_role} cannot create role {target_role}'},
                        error_code=403
                    )
            phone = data.get('phone')
            # phone required
            if not phone:
                return custom_response_obj(
                    message={'msg': 'Phone number is required'},
                    code=400,
                    error_msg={'msg': 'Phone number is required'},
                    error_code=400
                )
            # remove +91 if present
            # if phone.startswith("+91"):
            #     phone = phone[3:]
            # phone must be 10 digits
            if not phone.isdigit() or len(phone) != 10:
                return custom_response_obj(
                    message={'msg': 'Phone number must be 10 digits'},
                    code=400,
                    error_msg={'msg': 'Phone number must be 10 digits'},
                    error_code=400
                )
            
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            name_pattern = r'^[A-Za-z ]+$'
            if first_name and not re.match(name_pattern, first_name):
                return custom_response_obj(
                    message={'msg': 'First name should contain only alphabets'},
                    code=400,
                    error_msg={'msg': 'First name should contain only alphabets'},
                    error_code=400
                )
            if last_name and not re.match(name_pattern, last_name):
                return custom_response_obj(
                    message={'msg': 'Last name should contain only alphabets'},
                    code=400,
                    error_msg={'msg': 'Last name should contain only alphabets'},
                    error_code=400
                )
            # duplicate phone validation
            if User.objects.filter(phone=data.get('phone')).exists():
                return custom_response_obj(
                    message={'msg': 'User with this phone number already exists'},
                    code=400,
                    error_msg={'msg': 'User with this phone number already exists'},
                    error_code=400
                )
            # 🔹 Add pincode validation here
            pincode = data.get("pincode")
            if pincode:
                if not pincode.isdigit() or len(pincode) != 6:
                    return custom_response_obj(
                        message={'msg': 'Pincode must be 6 digits'},
                        code=400,
                        error_msg={'msg': 'Pincode must be 6 digits'},
                        error_code=400
                    )
            # email validation
            email = data.get("email")
            if email and User.objects.filter(email=email).exists():
                return custom_response_obj(
                    message={'msg': 'User with this email already exists'},
                    code=400,
                    error_msg={'msg': 'User with this email already exists'},
                    error_code=400
                )
            # employee id validation
            employee_id = data.get("employee_id")
            if employee_id and User.objects.filter(employee_id=employee_id).exists():
                return custom_response_obj(
                    message={'msg': 'User with this employee ID already exists'},
                    code=400,
                    error_msg={'msg': 'User with this employee ID already exists'},
                    error_code=400
                    )
            exclude_from_bt_date_logic = data.get("exclude_from_bt_date_logic", False)
            if not isinstance(exclude_from_bt_date_logic, bool):
                return custom_response_obj(
                    message={'msg': 'exclude_from_bt_date_logic must be a boolean'},
                    code=400,
                    error_msg={'msg': 'exclude_from_bt_date_logic must be a boolean'},
                    error_code=400
                )
            if exclude_from_bt_date_logic and target_role != ROLES.SALES_OFFICER.value:
                return custom_response_obj(
                    message={'msg': 'exclude_from_bt_date_logic is only available for Sales Officer users'},
                    code=400,
                    error_msg={'msg': 'exclude_from_bt_date_logic is only available for Sales Officer users'},
                    error_code=400
                )
            username = data.get("username")
            if username:
                sanitized_username = self.sanitize_username(username)
                if not sanitized_username:
                    return custom_response_obj(
                        message={'msg': 'Username is invalid'},
                        code=400,
                        error_msg={'msg': 'Username is invalid'},
                        error_code=400
                    )
                if User.objects.filter(username=sanitized_username).exists():
                    return custom_response_obj(
                        message={'msg': 'User with this username already exists'},
                        code=400,
                        error_msg={'msg': 'User with this username already exists'},
                        error_code=400
                    )
                data['username'] = sanitized_username
            branch_id = data.pop('branch_id', None)
            assigned_to = data.pop('assigned_to', None)
            if assigned_to:
                data['assign_so_id'] = assigned_to
                
            user = self.register_user(
                data,
                send_welcome_email=send_welcome_email,
                initialize_password=initialize_password,
            )
            if branch_id:
                branch_map = BranchUserMapping(user=user, branch_id=branch_id)
                branch_map.save()
            serializer = UserEmployeeResponseSerializer(user)
            return custom_response_obj(message=serializer.data, code=200)
        except Exception as e:
            log.exception("[POST | UserService Exception] Error - {error}".format(error=e))
            return custom_response_obj(
                message={'msg': str(e)},
                code=500,
                error_msg={'msg': str(e)},
                error_code=500
            )
        
    def delete_user(self, user_id, actor_role=None):
        try:
            if not user_id:
                return custom_response_obj(
                    message={"msg": "user_id is required"},
                    code=400,
                    error_msg={"msg": "user_id is required"},
                    error_code=400
                )
            user = User.objects.get(user_id=user_id)
            if actor_role == ROLES.TELE_ADMIN.value and user.role != ROLES.TELE_USER.value:
                return custom_response_obj(
                    message={"msg": "TELE_ADMIN can only inactivate TELE_USER accounts"},
                    code=403,
                    error_msg={"msg": "TELE_ADMIN can only inactivate TELE_USER accounts"},
                    error_code=403
                )
            user.is_active = False
            user.save(update_fields=["is_active"])
            return custom_response_obj(
                message={"msg": "User marked inactive successfully"},
                code=200
            )
        except User.DoesNotExist:
            return custom_response_obj(
                message={"msg": "User not found"},
                code=404,
                error_msg={"msg": "User not found"},
                error_code=404
            )
