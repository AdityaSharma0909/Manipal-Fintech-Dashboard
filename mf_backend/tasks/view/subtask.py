from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from tasks.models import SubTask, SubTaskApproval, StepCorrection
from tasks.serializers import SubTaskSerializer, GetSubTaskSerializer
from utils.responseHandler import HttpResponse
import traceback
import csv
import pandas as pd
from io import BytesIO as IO
from django.http import HttpResponse as dhttp
from django.db import transaction
from io import TextIOWrapper
from users.models import User
from utils.constants import ROLES, TASK_STATUS, SUBTASK_STATUS, CENTRAL_OPS_STATUS
from django.db.models import Q, Case, When, IntegerField, Count
from tasks.view.permissions import can_access_task

class SubTaskView(APIView):
    permission_classes = []

    @extend_schema(
        summary="Get list of subtasks",
        description="Fetch subtasks with optional filtering by task, assign_to, and status.",
        parameters=[
            OpenApiParameter(name="pg", type=int, description="Page number for pagination", default=1),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search across `sub_task_id`, `organisation_name`, and `contact_person_name`. Example: `ST_00001` or `Acme Corp`.",
            ),
            OpenApiParameter(name="id", type=str, description="Filter by subtask UUID"),
            OpenApiParameter(name="sub_task_id", type=str, description="Filter by subtask ID (e.g., ST_00001)"),
            OpenApiParameter(name="assign_to", type=str, description="Filter by user UUID assigned to the subtask"),
            OpenApiParameter(name="assign_to_username", type=str, description="Filter by username assigned to the subtask"),
            OpenApiParameter(name="assign_to_employee_id", type=str, description="Filter by employee ID assigned to the subtask"),
            OpenApiParameter(name="task", type=str, description="Filter by task UUID"),
            OpenApiParameter(name="task_id", type=str, description="Filter by task ID (e.g., TASK_001)"),
            OpenApiParameter(name="status", type=str, description="Filter by subtask status (NEW_TASK, IN_PROGRESS, COMPLETED)"),
            OpenApiParameter(name="priority", type=str, description="Filter by task priority (HIGH, MEDIUM, LOW)"),
            OpenApiParameter(name="reward_amount", type=str, description="Filter by total reward assigned (0-500, 500-1500, Above 1500)"),
            OpenApiParameter(name="flow_action", type=str, description="Filter by flow ID or flow description"),
        ],
        responses={200: GetSubTaskSerializer(many=True)}
    )
    def get(self, request):
        try:
            user = request.user
            params = request.query_params
            query = {}
            page_limit = 10  # pagination limit

            pg = request.GET.get("pg", "1")
            subtask_uuid = request.GET.get("id") # Renamed to avoid conflict with sub_task_id
            sub_task_id = request.GET.get("sub_task_id")
            assign_to_uuid = request.GET.get("assign_to") # Renamed to avoid conflict with assign_to_username/employee_id
            assign_to_username = request.GET.get("assign_to_username")
            assign_to_employee_id = request.GET.get("assign_to_employee_id")
            task_uuid = request.GET.get("task") # Renamed to avoid conflict with task_id
            task_id = request.GET.get("task_id")
            status = request.GET.get("status")
            priority = request.GET.get("priority")
            reward_amount = request.GET.get("reward_amount")
            flow_action = request.GET.get("flow_action")
            search = request.GET.get("search")

            # pagination
            try:
                page_no = int(pg)
                offset = (page_no - 1) * page_limit
            except ValueError:
                return HttpResponse.BadRequest("Please send correct 'pg' param.")

            # filters
            if subtask_uuid:
                query["id"] = subtask_uuid
            if sub_task_id:
                query["sub_task_id"] = sub_task_id
            if assign_to_uuid:
                query["assign_to__user_id"] = assign_to_uuid
            if assign_to_username:
                query["assign_to__username"] = assign_to_username
            if assign_to_employee_id:
                query["assign_to__employee_id"] = assign_to_employee_id
            if task_uuid:
                query["task__id"] = task_uuid
            if task_id:
                query["task__task_id"] = task_id
            if priority:
                query["task__priority"] = priority
            # status filter needs special handling for NEW_TASK
            if status and status != SUBTASK_STATUS.NEW_TASK.value:
                query["status"] = status

            # reward range filter
            if reward_amount:
                if reward_amount == "0-500":
                    query["task__total_reward_assigned__gte"] = 0
                    query["task__total_reward_assigned__lte"] = 500
                elif reward_amount == "500-1500":
                    query["task__total_reward_assigned__gte"] = 500
                    query["task__total_reward_assigned__lte"] = 1500
                elif reward_amount == "Above 1500":
                    query["task__total_reward_assigned__gte"] = 1500

            # Execute query based on role
            if user.role == ROLES.SALES_OFFICER.value:
                # Show subtasks assigned to the SO or their agents
                queryset = (
                    SubTask.objects
                    .filter(Q(assign_to=user) | Q(assign_to__assign_so=user), **query)
                )
            elif user.role == ROLES.TELE_ADMIN.value:
                # Tele Admin: subtasks from tasks created by user, matching user's team, or created by Tele Users under them
                tele_q = Q(task__created_by=user)
                if getattr(user, 'team', None):
                    tele_q |= Q(task__team=user.team)
                # Include subtasks from tasks created by Tele Users who report to this Tele Admin
                tele_user_ids = User.objects.filter(
                    role=ROLES.TELE_USER.value,
                    assign_so=user
                ).values_list('user_id', flat=True)
                if tele_user_ids:
                    tele_q |= Q(task__created_by__user_id__in=tele_user_ids)
                queryset = SubTask.objects.filter(tele_q, **query)
            elif user.role == ROLES.TELE_USER.value:
                # Tele User: subtasks from tasks created by user only
                queryset = SubTask.objects.filter(task__created_by=user, **query)
            else:
                queryset = SubTask.objects.filter(**query)

            # ✅ If status filter is NEW_TASK, include null status
            if status == SUBTASK_STATUS.NEW_TASK.value:
                queryset = queryset.filter(Q(status=status) | Q(status__isnull=True))

            # Flow Action Filter (IContains search across multiple fields)
            if flow_action:
                flow_list = [f.strip() for f in flow_action.split(",") if f.strip()]
                if flow_list:
                    flow_q = Q()
                    for f in flow_list:
                        flow_q |= Q(task__task_flow_entries__flow__flow_id__icontains=f) | \
                                  Q(task__task_flow_entries__flow__flow_description__icontains=f)
                    queryset = queryset.filter(flow_q).distinct()

            if search:
                search_q = Q(sub_task_id__icontains=search) | Q(organisation_name__icontains=search) | Q(contact_person_name__icontains=search)
                queryset = queryset.filter(search_q)

            # Exclude closed and declined tasks
            queryset = (
                queryset
                .exclude(task__status=TASK_STATUS.CLOSED.value)
                .exclude(status=SUBTASK_STATUS.DECLINED.value)
                .select_related("task", "assign_to")
                .order_by("-created_at", "-id")
            )

            # Get total count before pagination
            total_count = queryset.count()

            # ✅ Calculate status_counts for the entire queryset (unpaginated)
            # Use base_queryset (before status filter) to get counts of ALL statuses
            if status:
                # We need a base queryset without the status filter applied
                base_query_params = {k:v for k,v in query.items() if k not in ['status', 'sub_task_id', 'assign_to__username', 'assign_to__employee_id', 'task__task_id']}
                
                if user.role == ROLES.SALES_OFFICER.value:
                    base_queryset = SubTask.objects.filter(Q(assign_to=user) | Q(assign_to__assign_so=user), **base_query_params)
                elif user.role == ROLES.TELE_ADMIN.value:
                    tele_q = Q(task__created_by=user)
                    if getattr(user, 'team', None): tele_q |= Q(task__team=user.team)
                    tele_user_ids = User.objects.filter(role=ROLES.TELE_USER.value, assign_so=user).values_list('user_id', flat=True)
                    if tele_user_ids: tele_q |= Q(task__created_by__user_id__in=tele_user_ids)
                    base_queryset = SubTask.objects.filter(tele_q, **base_query_params)
                elif user.role == ROLES.TELE_USER.value:
                    base_queryset = SubTask.objects.filter(task__created_by=user, **base_query_params)
                else:
                    base_queryset = SubTask.objects.filter(**base_query_params)
                
                base_queryset = base_queryset.exclude(task__status=TASK_STATUS.CLOSED.value).exclude(status=SUBTASK_STATUS.DECLINED.value)

                # ✅ Re-apply flow_action filter to base_queryset if present
                if flow_action:
                    flow_list = [f.strip() for f in flow_action.split(",") if f.strip()]
                    if flow_list:
                        flow_q = Q()
                        for f in flow_list:
                            flow_q |= Q(task__task_flow_entries__flow__flow_id__icontains=f) | \
                                      Q(task__task_flow_entries__flow__flow_description__icontains=f)
                        base_queryset = base_queryset.filter(flow_q).distinct()
                        
                if search:
                    base_queryset = base_queryset.filter(search_q)
            else:
                base_queryset = queryset

            status_counts = {
                SUBTASK_STATUS.NEW_TASK.value: base_queryset.filter(Q(status=SUBTASK_STATUS.NEW_TASK.value) | Q(status__isnull=True)).count(),
                SUBTASK_STATUS.IN_PROGRESS.value: base_queryset.filter(status=SUBTASK_STATUS.IN_PROGRESS.value).count(),
                SUBTASK_STATUS.COMPLETED.value: base_queryset.filter(status=SUBTASK_STATUS.COMPLETED.value).count(),
            }


            # ✅ Return single object if subtask_id is provided
            if subtask_uuid and not sub_task_id: # Use subtask_uuid for single object retrieval if sub_task_id is not provided
                subtask = queryset.first()
                if not subtask:
                    return HttpResponse.BadRequest("SubTask not found")
                serializer = GetSubTaskSerializer(subtask, context={"request": request})  # ✅ context added
                return HttpResponse.Success({"subtask": serializer.data, "total_count": 1})

            # ✅ Return paginated list
            data = queryset[offset: offset + page_limit]
            serializer = GetSubTaskSerializer(data, many=True, context={"request": request})

            return HttpResponse.Success({
                "subtask_trackers": serializer.data,
                "subtasks": serializer.data,
                "status_counts": status_counts,
                "total_count": total_count
            })




        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


    @extend_schema(
        summary="Create a new subtask",
        description="Create a new subtask for a given task. If sub_task_id is not provided, it will be auto-generated.",
        request=SubTaskSerializer,
        responses={201: SubTaskSerializer}
    )
    def post(self, request):
        try:
            data = request.data.copy()
            user = request.user

            if not data.get("sub_task_id"):
                from django.db.models import Max
                last_subtask = SubTask.objects.filter(sub_task_id__startswith="ST_").aggregate(Max("sub_task_id"))["sub_task_id__max"]
                if last_subtask:
                    try:
                        last_sequence = int(last_subtask.split("_")[1])
                    except (IndexError, ValueError):
                        last_sequence = 0
                else:
                    last_sequence = 0
                
                data["sub_task_id"] = f"ST_{last_sequence + 1:05d}"

            data["created_by"] = str(user.user_id)
            data["modified_by"] = str(user.user_id)

            serializer = SubTaskSerializer(data=data)
            if serializer.is_valid():
                serializer.save(created_by=user, modified_by=user)
                return HttpResponse.Success({"subtask": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    @extend_schema(
        summary="Update subtasks (partial)",
        description="Update one or more subtasks. Input can be a single object or a list of objects. Each object must include 'subtask_id'.",
        request=SubTaskSerializer(many=True),
        responses={200: SubTaskSerializer(many=True)}
    )
    def patch(self, request):
        try:
            data = request.data

            # ✅ Normalize input to always be a list
            if isinstance(data, dict):
                data = [data]
            elif not isinstance(data, list):
                return HttpResponse.BadRequest("Invalid data format — must be an object or list of objects")

            updated_subtasks = []

            for item in data:
                subtask_id = item.get("subtask_id")
                if not subtask_id:
                    return HttpResponse.BadRequest("Each item must include 'subtask_id'")

                try:
                    subtask = SubTask.objects.get(id=subtask_id)
                except SubTask.DoesNotExist:
                    return HttpResponse.BadRequest(f"SubTask with id {subtask_id} not found")

                if not can_access_task(request.user, subtask.task):
                    return HttpResponse.BadRequest("You do not have permission to update this subtask.")

                serializer = SubTaskSerializer(subtask, data=item, partial=True)
                if serializer.is_valid():
                    serializer.save(modified_by=request.user)
                    updated_subtasks.append(serializer.data)
                else:
                    return HttpResponse.BadRequest(serializer.errors)

            return HttpResponse.Success({
                "message": "Subtasks updated successfully",
                "total_updated": len(updated_subtasks),
                "updated_subtasks": updated_subtasks
            })

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    @extend_schema(
        summary="Delete a subtask",
        description="Delete a subtask by its ID.",
        parameters=[
            OpenApiParameter(name="subtask_id", type=str, description="The UUID of the subtask to delete", required=True),
        ],
        responses={200: {"msg": "SubTask deleted successfully"}}
    )
    def delete(self, request):
        try:
            subtask_id = request.GET.get("subtask_id", "")
            if not subtask_id:
                return HttpResponse.BadRequest("subtask_id is required!")

            subtask = SubTask.objects.get(id=subtask_id)

            if not can_access_task(request.user, subtask.task):
                return HttpResponse.BadRequest("You do not have permission to delete this subtask.")

            subtask.delete()
            return HttpResponse.Success({"msg": "SubTask deleted successfully"})
        except SubTask.DoesNotExist:
            return HttpResponse.BadRequest("SubTask not found")


class SubTaskExportAPIView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            user = request.user
            query = {}

            subtask_id = request.GET.get("id")
            assign_to = request.GET.get("assign_to")
            task = request.GET.get("task")
            status = request.GET.get("status")

            if subtask_id:
                query["id"] = subtask_id
            if assign_to:
                query["assign_to__user_id"] = assign_to
            if task:
                query["task__id"] = task
            if status:
                query["status"] = status

            if user.role == ROLES.SALES_OFFICER.value:
                queryset = (
                    SubTask.objects
                    .filter(Q(assign_to=user) | Q(assign_to__assign_so=user), **query)
                )
            elif user.role == ROLES.TELE_ADMIN.value:
                tele_q = Q(task__created_by=user)
                if getattr(user, 'team', None):
                    tele_q |= Q(task__team=user.team)
                tele_user_ids = User.objects.filter(
                    role=ROLES.TELE_USER.value,
                    assign_so=user
                ).values_list('user_id', flat=True)
                if tele_user_ids:
                    tele_q |= Q(task__created_by__user_id__in=tele_user_ids)
                queryset = SubTask.objects.filter(tele_q, **query)
            elif user.role == ROLES.TELE_USER.value:
                queryset = SubTask.objects.filter(task__created_by=user, **query)
            else:
                queryset = SubTask.objects.filter(**query)

            queryset = (
                queryset
                .select_related("task", "assign_to")
                .prefetch_related("trackers__flow")
                .order_by("-created_at", "-id")
            )

            rows = []
            for subtask in queryset:
                # Get the latest tracker for customer details
                latest_tracker = subtask.trackers.order_by("-created_at").first()
                
                all_trackers = subtask.trackers.all()
                flow_ids = []
                flow_descriptions = []
                for t in all_trackers:
                    if getattr(t, 'flow', None):
                        fid = str(t.flow.flow_id) if t.flow.flow_id else ""
                        fdesc = str(t.flow.flow_description) if t.flow.flow_description else ""
                        if fid and fid not in flow_ids:
                            flow_ids.append(fid)
                        if fdesc and fdesc not in flow_descriptions:
                            flow_descriptions.append(fdesc)

                rows.append({
                    "SubTask UUID": str(subtask.id),
                    "SubTask ID": subtask.sub_task_id,
                    "Task UUID": str(subtask.task.id) if subtask.task else "",
                    "Task ID": subtask.task.task_id if subtask.task else "",
                    "Task Summary": subtask.task.task_summary if subtask.task else "",
                    "Task Status": subtask.task.status if subtask.task else "",
                    "Task Priority": subtask.task.priority if subtask.task else "",
                    "Flow ID": ", ".join(flow_ids) if flow_ids else "",
                    "Flow Description": ", ".join(flow_descriptions) if flow_descriptions else "",
                    "Organisation Name": subtask.organisation_name,
                    "Contact Person": subtask.contact_person_name,
                    "Contact Number": subtask.registered_mobile_number,
                    "Address Line 1": subtask.address_line_1,
                    "Address Line 2": subtask.address_line_2,
                    "Pincode": subtask.pincode,
                    "City": subtask.city,
                    "District": subtask.district,
                    "State": subtask.state,
                    "Status": subtask.status,
                    "Assigned To": f"{subtask.assign_to.first_name or ''} {subtask.assign_to.last_name or ''}".strip() if subtask.assign_to else "",
                    # "Assigned Username": subtask.assign_to.username if subtask.assign_to else "",
                    "Assigned Employee ID": subtask.assign_to.employee_id if subtask.assign_to else "",
                    "Type of User": subtask.type_of_user,
                    "Entity Type": subtask.entity_type,
                    "Unique ID": subtask.unique_id,
                    "Verification ID": subtask.verification_id,
                    "Registered Mobile": subtask.registered_mobile_number,
                    "OTP Verified": "Yes" if subtask.otp_verified else "No",
                    "Created At": subtask.created_at.strftime("%d %b, %Y, %I:%M %p") if subtask.created_at else "",
                    "Decline Reason": subtask.decline_reason or "",
                    # Fields from latest tracker
                    "Customer Full Name": latest_tracker.full_name if latest_tracker else "",
                    "PAN Number": latest_tracker.pan_number if latest_tracker else "",
                    "Aadhar Number": latest_tracker.aadhar_number if latest_tracker else "",
                    "Customer Phone": subtask.registered_mobile_number,
                    "Customer Email": latest_tracker.email if latest_tracker else "",
                    "Product Category": latest_tracker.product_category if latest_tracker else "",
                    "Product Sub Category": latest_tracker.product_sub_category if latest_tracker else "",
                    "Amount": float(latest_tracker.amount) if latest_tracker and latest_tracker.amount else 0,
                    "Lead Source": latest_tracker.lead_source if latest_tracker else "",
                    # Lead Closure details (from latest tracker)
                    "Lead Closure Customer ID": latest_tracker.customer_id if latest_tracker else "",
                    "Lead Closure Loan Date": latest_tracker.loan_date.isoformat() if latest_tracker and latest_tracker.loan_date else "",
                    "Lead Closure Loan Account": latest_tracker.loan_account_number if latest_tracker else "",
                    "Lead Closure Bank Name": latest_tracker.bank_name if latest_tracker else "",
                    "Lead Closure Type": latest_tracker.lead_type if latest_tracker else ""
                })

            # define explicit header order and force headers even when there is no data
            headers = [
                "SubTask ID", "Task ID", "Task Summary", "Task Status", "Task Priority",
                "Flow ID", "Flow Description",
                "Organisation Name", "Contact Person", "Contact Number",
                "Address Line 1", "Address Line 2", "Pincode", "City", "District", "State",
                "Status", "Assigned To", "Assigned Employee ID", "Type of User", "Entity Type",
                "Unique ID", "Verification ID", "Registered Mobile", "OTP Verified", "Created At",
                "Decline Reason",
                "Customer Full Name", "PAN Number", "Aadhar Number", "Customer Phone", "Customer Email",
                "Product Category", "Product Sub Category", "Amount", "Lead Source",
                "Lead Closure Customer ID", "Lead Closure Loan Date", "Lead Closure Loan Account",
                "Lead Closure Bank Name", "Lead Closure Type"
            ]
            df = pd.DataFrame(rows, columns=headers)
            excel_file = IO()
            xlwriter = pd.ExcelWriter(excel_file, engine='openpyxl')
            df.to_excel(xlwriter, 'SubTasks Report', index=False, header=True)
            xlwriter.close()
            excel_file.seek(0)

            response = dhttp(
                excel_file.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'
            response['Content-Disposition'] = 'attachment; filename=SubTasks_Data.xlsx'

            return response

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class SubTaskDeclineAPIView(APIView):
    permission_classes = []
    @extend_schema(
        summary="Decline a subtask",
        description="Mark a subtask as DECLINED and provide a reason.",
        request={"application/json": {"type": "object", "properties": {"subtask_id": {"type": "string"}, "decline_reason": {"type": "string"}}}},
        responses={200: {"message": "SubTask declined successfully"}}
    )
    def post(self, request):
        try:
            subtask_id = request.data.get("subtask_id") or request.GET.get("subtask_id")
            if not subtask_id:
                return HttpResponse.BadRequest("subtask_id is required")
            subtask = SubTask.objects.get(id=subtask_id)

            if not can_access_task(request.user, subtask.task):
                return HttpResponse.BadRequest("You do not have permission to decline this subtask.")

            subtask.status = SUBTASK_STATUS.DECLINED.value
            decline_reason = request.data.get("decline_reason") or request.GET.get("decline_reason")
            if decline_reason is not None:
                subtask.decline_reason = decline_reason
            subtask.modified_by = request.user
            if decline_reason is not None:
                subtask.save(update_fields=["status", "decline_reason", "modified_by"])
            else:
                subtask.save(update_fields=["status", "modified_by"])
            task = subtask.task
            total = task.subtasks.count()
            completed_count = task.subtasks.filter(status=SUBTASK_STATUS.COMPLETED.value).count()
            in_progress_exists = task.subtasks.filter(status=SUBTASK_STATUS.IN_PROGRESS.value).exists()
            if completed_count == total and total > 0:
                task.status = TASK_STATUS.COMPLETED.value
                task.progress = 100
                task.completed = True
            else:
                task.status = TASK_STATUS.IN_PROGRESS.value if (in_progress_exists or completed_count > 0) else TASK_STATUS.YET_TO_START.value
                task.progress = (completed_count * 100) // total if total > 0 else 0
                task.completed = False
            task.modified_by = request.user
            task.save(update_fields=["status", "progress", "completed", "modified_by"])
            return HttpResponse.Success({"message": "SubTask declined successfully"})
        except SubTask.DoesNotExist:
            return HttpResponse.BadRequest("SubTask not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class SubTaskDetailedView(APIView):
    permission_classes = []
    @extend_schema(
        summary="Get detailed subtask info",
        description="Fetch detailed information for a single subtask by its UUID.",
        parameters=[
            OpenApiParameter(name="subtask_id", type=str, description="The UUID of the subtask", required=True),
        ],
        responses={200: GetSubTaskSerializer}
    )
    def get(self, request):
        user = request.user
        try:
            subtask_id = request.GET.get("subtask_id", "")
            if not subtask_id:
                return HttpResponse.BadRequest("subtask_id is required!")

            subtask = SubTask.objects.get(id=subtask_id)

            if not can_access_task(request.user, subtask.task):
                return HttpResponse.BadRequest("You do not have permission to view this subtask.")

            serializer = GetSubTaskSerializer(subtask)
            return HttpResponse.Success({"subtask": serializer.data})

        except SubTask.DoesNotExist:
            return HttpResponse.BadRequest("SubTask not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class AssignSubTaskAPIView(APIView):
    def post(self, request):
        try:
            user = request.user
            data = request.data
            file = request.FILES.get("user_details")
            
            task_id = request.GET.get("task_id", "")
            if not task_id:
                return HttpResponse.BadRequest("task_id is required!")
            
            # Fetch subtasks for the given task_id, ordered by sub_task_id
            subtasks_queryset = SubTask.objects.filter(task__id=task_id).order_by("sub_task_id")
            if not subtasks_queryset.exists():
                return HttpResponse.BadRequest({"error": "No subtasks found for the given task_id"})

            assignment_mapping = [] # List of (subtask_obj, user_obj)
            all_involved_users = [] # For the response 'users' field

            # ✅ If CSV file is uploaded
            if file:
                try:
                    csv_file = TextIOWrapper(file.file, encoding="utf-8")
                    reader = csv.DictReader(csv_file)
                    csv_rows = list(reader)
                    if not csv_rows:
                        return HttpResponse.BadRequest({"error": "CSV file is empty or contains no data rows."})
                    
                    # Identify relevant columns
                    subtask_id_col = next((h for h in reader.fieldnames if h.strip().lower() in ["subtask id", "sub_task_id", "sub task id"]), None)
                    employee_id_col = next((h for h in reader.fieldnames if h.strip().lower() in ["employee id", "employee_id", "user id", "user_id"]), None)
                    
                    if not employee_id_col:
                         return HttpResponse.BadRequest({"error": "No Employee ID or User ID column found in the CSV file"})

                    if subtask_id_col:
                        # Case 1: Direct mapping based on Subtask ID column
                        # 1. Get all unique SID and EID to fetch objects in batch
                        subtask_ids = list(set([row.get(subtask_id_col, "").strip() for row in csv_rows if row.get(subtask_id_col)]))
                        employee_ids = list(set([row.get(employee_id_col, "").strip() for row in csv_rows if row.get(employee_id_col)]))
                        
                        # 2. Fetch all involved subtasks (belonging to this task) and users
                        st_map = {st.sub_task_id: st for st in SubTask.objects.filter(sub_task_id__in=subtask_ids, task__id=task_id)}
                        u_map = {u.employee_id: u for u in User.objects.filter(employee_id__in=employee_ids)}
                        all_involved_users = list(u_map.values())
                        
                        # 3. Create mapping based on CSV rows
                        for row in csv_rows:
                            sid = row.get(subtask_id_col, "").strip()
                            eid = row.get(employee_id_col, "").strip()
                            if sid in st_map and eid in u_map:
                                assignment_mapping.append((st_map[sid], u_map[eid]))
                    else:
                        # Case 2: Positional mapping: First task to first user in CSV
                        # 1. Get list of unique Employee IDs from the CSV rows while maintaining order
                        unique_employee_ids = []
                        seen_eids = set()
                        for row in csv_rows:
                            eid = row.get(employee_id_col, "").strip()
                            if eid and eid not in seen_eids:
                                unique_employee_ids.append(eid)
                                seen_eids.add(eid)
                        
                        if not unique_employee_ids:
                             return HttpResponse.BadRequest({"error": "No Employee IDs found in the CSV file"})
                        
                        # 2. Fetch users and maintain CSV order
                        u_map = {u.employee_id: u for u in User.objects.filter(employee_id__in=unique_employee_ids)}
                        ordered_users = []
                        for eid in unique_employee_ids:
                            if eid in u_map:
                                ordered_users.append(u_map[eid])
                        
                        if not ordered_users:
                            return HttpResponse.BadRequest({"error": "No matching users found for the given Employee IDs"})
                        
                        all_involved_users = ordered_users
                        
                        # 3. Round-robin assignment based on subtasks ordered by sub_task_id
                        subtasks = list(subtasks_queryset)
                        total_users = len(ordered_users)
                        for i, st in enumerate(subtasks):
                            assigned_user = ordered_users[i % total_users]
                            assignment_mapping.append((st, assigned_user))

                except Exception as e:
                    traceback.print_exc()
                    return HttpResponse.BadRequest({"error": f"Failed to read CSV file: {str(e)}"})

            # ✅ Else use filter-based query
            else:
                state = data.get("state", "")
                if hasattr(data, "getlist"):
                    district = data.getlist("district", [])
                    city = data.getlist("city", [])
                    team = data.getlist("team", [])
                    badge = data.getlist("badge", [])
                    designation = data.getlist("designation", [])
                else:
                    district = data.get("district", []) or []
                    city = data.get("city", []) or []
                    team = data.get("team", []) or []
                    badge = data.get("badge", []) or []
                    designation = data.get("designation", []) or []

                filters = {}
                if state:
                    filters["state__iexact"] = state
                if district:
                    filters["district__in"] = district if isinstance(district, list) else [district]
                if city:
                    filters["city__in"] = city if isinstance(city, list) else [city]
                if team:
                    filters["team__in"] = team if isinstance(team, list) else [team]
                if badge:
                    filters["badge__in"] = badge if isinstance(badge, list) else [badge]
                if designation:
                    filters["designation__in"] = designation if isinstance(designation, list) else [designation]

                all_involved_users = list(User.objects.filter(**filters).order_by("first_name"))

                if not all_involved_users:
                    return HttpResponse.BadRequest({"error": "No users found for given filters"})
                
                # Round-robin assignment
                subtasks = list(subtasks_queryset)
                total_users = len(all_involved_users)
                for i, st in enumerate(subtasks):
                    assigned_user = all_involved_users[i % total_users]
                    assignment_mapping.append((st, assigned_user))

            # 🧩 Prepare user info for response
            user_info = [
                {
                    "user_id": str(u.user_id),
                    "employee_id": u.employee_id,
                    "full_name": f"{u.first_name or ''} {u.last_name or ''}".strip()
                }
                for u in all_involved_users
            ]

            # 🌀 Execute assignment
            assignment_results = []
            with transaction.atomic():
                for subtask, assigned_user in assignment_mapping:
                    subtask.assign_to = assigned_user
                    subtask.modified_by = user
                    subtask.save()

                    assignment_results.append({
                        "subtask_id": str(subtask.id),
                        "sub_task_id": subtask.sub_task_id,
                        "assigned_user_id": str(assigned_user.user_id),
                        "assigned_user_name": f"{assigned_user.first_name or ''} {assigned_user.last_name or ''}".strip(),
                        "assigned_user_employee_id": assigned_user.employee_id,
                    })

            # Final response
            return HttpResponse.Success({
                "message": "Subtasks assigned successfully",
                "total_users": len(all_involved_users),
                "users": user_info,
                "total_subtasks": subtasks_queryset.count(),
                "total_assigned": len(assignment_results),
                "assignments": assignment_results
            })

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
        
        
        
class ReassignSubTaskAPIView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            user = request.user
            data = request.data

            subtask_id = data.get("subtask_id")
            new_user_id = data.get("assign_to")

            if not subtask_id or not new_user_id:
                return HttpResponse.BadRequest("subtask_id and assign_to are required")

            # 1. Fetch subtask
            try:
                subtask = SubTask.objects.get(id=subtask_id)
            except SubTask.DoesNotExist:
                return HttpResponse.BadRequest("SubTask not found")

            # 2. Fetch new user
            try:
                new_user = User.objects.get(user_id=new_user_id)
            except User.DoesNotExist:
                return HttpResponse.BadRequest("User not found")

            # 3. Permission Check
            if user.role == ROLES.SALES_OFFICER.value:
                return HttpResponse.BadRequest("You are not allowed to reassign subtasks")

            # 4. Save old user (for response)
            old_user = subtask.assign_to

            # 5. Reassign
            subtask.assign_to = new_user
            subtask.status = None
            subtask.modified_by = user
            subtask.save(update_fields=["assign_to", "status", "modified_by"])

            return HttpResponse.Success({
                "message": "Subtask reassigned successfully",
                "subtask_id": str(subtask.id),
                "old_assigned_to": {
                    "user_id": str(old_user.user_id) if old_user else None,
                    "name": f"{old_user.first_name} {old_user.last_name}" if old_user else None,
                    "username": old_user.username
                    
                },
                "new_assigned_to": {
                    "user_id": str(new_user.user_id),
                    "name": f"{new_user.first_name} {new_user.last_name}",
                    "username": new_user.username

                }
            })

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class SubTaskSearchAPIView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            user = request.user
            params = request.query_params
            filters = {}

            # ---------------- Pagination ----------------
            page_limit = 10
            pg = params.get("pg", "1")

            try:
                page_no = int(pg)
                offset = (page_no - 1) * page_limit
            except:
                return HttpResponse.BadRequest("Invalid pg value")

            # ---------------- Filters ----------------
            if params.get("status"):
                filters["status"] = params.get("status")

            if params.get("task_id"):
                filters["task__id"] = params.get("task_id")

            if params.get("priority"):
                filters["task__priority"] = params.get("priority")

            # Sales officer sees only own subtasks
            if user.role == ROLES.SALES_OFFICER.value:
                filters["assign_to"] = user

            # Base queryset with filters excluding closed tasks
            queryset = (
                SubTask.objects
                .filter(**filters)
                .exclude(task__status=TASK_STATUS.CLOSED.value)
                .select_related("assign_to", "task")
                .order_by("sub_task_id")
            )

            # ---------------- Google/YouTube Style Search ----------------
            q = params.get("q", "").strip()

            if q:
                # Comprehensive search across ALL UI columns like Google/YouTube
                search_query = (
                    Q(sub_task_id__icontains=q) |
                    Q(unique_id__icontains=q) |                           
                    Q(contact_person_name__icontains=q) |                 
                    Q(contact_person_number__icontains=q) |                 
                    Q(organisation_name__icontains=q) |                   
                    Q(address_line_1__icontains=q) |                      
                    Q(address_line_2__icontains=q) |                      
                    Q(city__icontains=q) |                                
                    Q(assign_to__username__icontains=q) |
                    Q(assign_to__first_name__icontains=q) |
                    Q(assign_to__last_name__icontains=q) |
                    Q(assign_to__employee_id__icontains=q) |              
                    Q(status__icontains=q) |                              
                    Q(task__priority__icontains=q) |                      
                    Q(task__task_id__icontains=q) |                       
                    Q(pincode__icontains=q) |                             
                    Q(district__icontains=q) |                            
                    Q(state__icontains=q)                                 
                )
                
                queryset = queryset.filter(search_query).distinct()

            # ---------------- Pagination ----------------
            total = queryset.count()
            data = queryset[offset: offset + page_limit]

            serializer = GetSubTaskSerializer(
                data,
                many=True,
                context={"request": request}
            )

            return HttpResponse.Success({
                "total": total,
                "subtasks": serializer.data,
                "current_page": page_no,
                "page_limit": page_limit,
                "has_next": offset + page_limit < total
            })

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class ActiveUsersDropdownAPIView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            user = request.user
            params = request.query_params

            search = params.get("search", "").strip()

            # Sales Officer cannot reassign
            if user.role == ROLES.SALES_OFFICER.value:
                return HttpResponse.BadRequest(
                    "You are not allowed to reassign subtasks"
                )

            #  Only Agent + Sales Officer users
            users = User.objects.filter(
                is_active=True,
                role__in=[
                    ROLES.AGENT.value,
                    ROLES.SALES_OFFICER.value
                ]
            ).order_by("first_name")


            #  Search filter
            if search:
                users = users.filter(
                    Q(username__icontains=search) |
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(employee_id__icontains=search) |
                    Q(designation__icontains=search)
                )

            #  Limit & order
            users = users.order_by("first_name")

            #  Response data
            data = [
                {
                    "user_id": str(u.user_id),
                    "username": f"{u.first_name or ''} {u.last_name or ''}".strip(),
                    "employee_id": u.employee_id,
                    "designation": u.designation,
                    "role": u.role
                }
                for u in users
            ]

            return HttpResponse.Success({
                "count": len(data),
                "users": data
            })

        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
