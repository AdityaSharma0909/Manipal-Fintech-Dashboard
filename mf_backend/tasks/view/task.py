from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from tasks.models import Task, SubTask, TaskFlow
from flows.models import Flow
from tasks.serializers import TaskSerializer
import json
from utils.responseHandler import HttpResponse
import traceback
from django.db.models import Q, Sum
import csv
import io
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from datetime import datetime
from django.db.models import Max
import traceback
import uuid
from utils.constants import ROLES, SUBTASK_STATUS, TASK_STATUS
from users.models import User
from tasks.view.permissions import can_access_task


class TaskView(APIView):
    permission_classes = []

    @extend_schema(
        summary="List tasks",
        description=(
            "Returns paginated tasks. Supports filtering by status, created date range, "
            "flow action, assignee, and location, plus free-text search on task ID and task summary."
        ),
        parameters=[
            OpenApiParameter(
                name="pg",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number. Default is `1`.",
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by task status. Supports comma-separated values for multiple selection. Example: `YET_TO_START,IN_PROGRESS`.",
            ),
            OpenApiParameter(
                name="created_on",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by exact task creation date (YYYY-MM-DD). Example: `2024-03-25`.",
            ),
            OpenApiParameter(
                name="start_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by start date (YYYY-MM-DD). Example: `2024-01-01`.",
            ),
            OpenApiParameter(
                name="end_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by end date (YYYY-MM-DD). Example: `2024-03-31`.",
            ),
            OpenApiParameter(
                name="flow_action",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Filter by flow action using flow ID or flow description. "
                    "Supports comma-separated values. Example: `LOCATION_VERIFICATION,Lead Generation`."
                ),
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search across `task_id` and `task_summary`. Example: `TMS0325` or `Lead Verification`.",
            ),
            OpenApiParameter(
                name="assigned_to",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by assignee User ID or Employee ID. Example: `EMP1001` or `uuid-string`.",
            ),
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description="Filter by internal task UUID.",
            ),
            OpenApiParameter(
                name="priority",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by priority. Example: `HIGH`.",
            ),
            OpenApiParameter(
                name="state",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by state (comma separated for multiple). Example: `Karnataka,Maharashtra`.",
            ),
            OpenApiParameter(
                name="district",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by district (comma separated for multiple). Example: `Bangalore,Pune`.",
            ),
            OpenApiParameter(
                name="reward_amount",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by total reward assigned. Formats: `0-500`, `500-1500`, `Above 1500`, `min-max` (e.g., `0-200000`), `min+` (e.g., `1000000+`), or an exact number.",
            ),
        ],
    )
    def get(self, request):
        try:
            user = request.user
            params = request.query_params
            queryset = Task.objects.all()

            # Pagination
            limit = request.GET.get("limit")
            page_limit = int(limit) if limit and limit.isdigit() else 10
            pg = request.GET.get("pg", "1")
            try:
                page_no = int(pg)
                offset = (page_no - 1) * page_limit
            except ValueError:
                return HttpResponse.BadRequest("Invalid 'pg' param, must be integer.")

            # Multi-select Filters (Status and Flow Action)
            task_status = params.get("status")
            if task_status:
                status_list = [s.strip() for s in task_status.split(",") if s.strip()]
                if status_list:
                    queryset = queryset.filter(status__in=status_list)

            flow_action = params.get("flow_action")
            if flow_action:
                flow_list = [f.strip() for f in flow_action.split(",") if f.strip()]
                if flow_list:
                    flow_q = Q()
                    for f in flow_list:
                        flow_q |= Q(task_flow_entries__flow__flow_id__icontains=f) | \
                                  Q(task_flow_entries__flow__flow_description__icontains=f)
                    queryset = queryset.filter(flow_q)

            # Date Range Filters
            created_on = params.get("created_on")
            if created_on:
                try:
                    created_on_date = datetime.strptime(created_on, "%Y-%m-%d").date()
                    queryset = queryset.filter(created_at__date=created_on_date)
                except ValueError:
                    return HttpResponse.BadRequest("Invalid 'created_on' param, expected YYYY-MM-DD.")

            start_date = params.get("start_date")
            if start_date:
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                    queryset = queryset.filter(created_at__date__gte=start_date_obj)
                except ValueError:
                    return HttpResponse.BadRequest("Invalid 'start_date' param, expected YYYY-MM-DD.")

            end_date = params.get("end_date")
            if end_date:
                try:
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                    queryset = queryset.filter(created_at__date__lte=end_date_obj)
                except ValueError:
                    return HttpResponse.BadRequest("Invalid 'end_date' param, expected YYYY-MM-DD.")

            # Assignee Filter
            assigned_to = params.get("assigned_to")
            if assigned_to:
                # Check if assigned_to is a valid UUID to avoid filtering errors
                is_uuid = False
                try:
                    uuid.UUID(str(assigned_to))
                    is_uuid = True
                except (ValueError, AttributeError):
                    is_uuid = False

                if is_uuid:
                    assignee_q = Q(subtasks__assign_to__user_id=assigned_to) | \
                                 Q(subtasks__assign_to__employee_id__iexact=assigned_to)
                else:
                    # If not a UUID, only filter by employee_id
                    assignee_q = Q(subtasks__assign_to__employee_id__iexact=assigned_to)
                
                queryset = queryset.filter(assignee_q)

            # Search and Other Filters
            search = params.get("search")
            if search:
                queryset = queryset.filter(
                    Q(task_id__icontains=search) |
                    Q(task_summary__icontains=search)
                )

            task_id = params.get("id")
            if task_id:
                queryset = queryset.filter(id=task_id)

            priority = params.get("priority")
            if priority:
                queryset = queryset.filter(priority=priority)

            reward_amount_param = params.get("reward_amount")
            if reward_amount_param:
                try:
                    if reward_amount_param == "0-500":
                        queryset = queryset.filter(total_reward_assigned__gte=0, total_reward_assigned__lte=500)
                    elif reward_amount_param == "500-1500":
                        queryset = queryset.filter(total_reward_assigned__gte=500, total_reward_assigned__lte=1500)
                    elif reward_amount_param == "Above 1500":
                        queryset = queryset.filter(total_reward_assigned__gte=1500)
                    elif "-" in reward_amount_param:
                        min_val, max_val = reward_amount_param.split("-")
                        queryset = queryset.filter(total_reward_assigned__gte=int(min_val), total_reward_assigned__lte=int(max_val))
                    elif reward_amount_param.endswith("+"):
                        min_val = reward_amount_param[:-1]
                        queryset = queryset.filter(total_reward_assigned__gte=int(min_val))
                    else:
                        queryset = queryset.filter(total_reward_assigned=int(reward_amount_param))
                except ValueError:
                    return HttpResponse.BadRequest("Invalid 'reward_amount' format. Use '0-500', '500-1500', 'Above 1500', 'min-max', 'min+', or an exact number.")

            state = params.get("state")
            if state:
                states = [s.strip() for s in state.split(",") if s.strip()]
                if states:
                    queryset = queryset.filter(state__in=states)

            district = params.get("district")
            if district:
                districts = [d.strip() for d in district.split(",") if d.strip()]
                if districts:
                    queryset = queryset.filter(district__in=districts)

            # Sales Officer logic (Legacy restriction)
            if user.role == ROLES.SALES_OFFICER.value:
                # Only tasks that have subtasks assigned to this user
                assigned_task_ids = SubTask.objects.filter(assign_to=user).values_list("task_id", flat=True)
                if assigned_task_ids:
                    queryset = queryset.filter(id__in=assigned_task_ids)
                else:
                    return HttpResponse.Success({"tasks": [], "total_count": 0, "total_pages": 0, "current_page": page_no})

            # Tele Admin: tasks created by user, matching user's team, or created by Tele Users under them
            elif user.role == ROLES.TELE_ADMIN.value:
                tele_q = Q(created_by=user)
                if getattr(user, 'team', None):
                    tele_q |= Q(team=user.team)
                # Include tasks created by Tele Users who report to this Tele Admin
                tele_user_ids = User.objects.filter(
                    role=ROLES.TELE_USER.value,
                    assign_so=user
                ).values_list('user_id', flat=True)
                if tele_user_ids:
                    tele_q |= Q(created_by__user_id__in=tele_user_ids)
                queryset = queryset.filter(tele_q)

            # Tele User: tasks created by user only
            elif user.role == ROLES.TELE_USER.value:
                queryset = queryset.filter(created_by=user)

            # Query execution
            total_reward_sum = queryset.aggregate(total=Sum("total_reward_assigned"))["total"] or 0
            distinct_queryset = queryset.distinct().order_by("-created_at")
            total_count = distinct_queryset.count()
            tasks = distinct_queryset[offset: offset + page_limit]

            serializer = TaskSerializer(tasks, many=True, context={"request": request})
            return HttpResponse.Success({
                "tasks": serializer.data,
                "total_count": total_count,
                "total_pages": (total_count + page_limit - 1) // page_limit,
                "current_page": page_no,
                "reward_amount": total_reward_sum
            })

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))



    def post(self, request):
        try:
            data = request.data.copy()
            user = request.user

            # ✅ 0️⃣ Pre-read and validate CSV if provided
            csv_rows = []
            if "sub_task" in request.FILES:
                sub_task_file: InMemoryUploadedFile = request.FILES["sub_task"]
                try:
                    decoded_file = sub_task_file.read().decode("utf-8")
                    io_string = io.StringIO(decoded_file)
                    csv_reader = csv.DictReader(io_string)
                    csv_rows = list(csv_reader)

                    if not csv_rows:
                        return HttpResponse.BadRequest({"error": "CSV file is empty or contains no data rows."})
                except Exception as e:
                    return HttpResponse.BadRequest({"error": f"Failed to read CSV file: {str(e)}"})

            with transaction.atomic():

                # ✅ 1️⃣ Generate task_id
                today = datetime.now()
                prefix = "TMS"
                date_str = today.strftime("%m%d")  # MMDD format

                # Get the last task created today
                last_task = Task.objects.filter(
                    created_at__date=today.date()
                ).aggregate(Max("task_id"))["task_id__max"]

                if last_task:
                    # Extract the last 4 digits and increment
                    try:
                        last_sequence = int(last_task[-4:])
                    except ValueError:
                        last_sequence = 0
                    next_sequence = last_sequence + 1
                else:
                    next_sequence = 1

                # Format the new task_id
                task_id = f"{prefix}{date_str}{next_sequence:04d}"
                data["task_id"] = task_id
                # Parse task_flow_entries if present
                task_flow_entries = data.get("task_flow_entries")
                if task_flow_entries and isinstance(task_flow_entries, str):
                    try:
                        data["task_flow_entries"] = json.loads(task_flow_entries)
                    except json.JSONDecodeError:
                        return HttpResponse.BadRequest({"error": "Invalid JSON for task_flow_entries"})

                data["created_by"] = str(user.user_id)
                data["modified_by"] = str(user.user_id)

                # Save main Task
                serializer = TaskSerializer(data=data, context={"request": request})
                if not serializer.is_valid():
                    return HttpResponse.BadRequest(serializer.errors)

                task = serializer.save(created_by=user, modified_by=user, assigned_by=user)

                flow_entries = data.get("task_flow_entries", [])
                seen_flow_ids = set()
                for entry in flow_entries:
                    fid = entry.get("flow")
                    if fid in seen_flow_ids:
                        return HttpResponse.BadRequest("Duplicate flow creation is not allowed in Task.")
                    seen_flow_ids.add(fid)

                for i, tfd in enumerate(flow_entries):
                    try:
                        flow_obj = Flow.objects.get(id=tfd["flow"])
                        TaskFlow.objects.create(
                            task=task,
                            flow=flow_obj,
                            condition=tfd.get("condition", "MANDATORY"),
                            reward=tfd.get("reward", 0),  # Always use reward from frontend
                            order=tfd.get("order", i)
                        )
                    except Flow.DoesNotExist:
                        continue

                # Handle CSV file upload for SubTasks
                if csv_rows:
                    # Get the last sub_task_id to generate new ones
                    last_subtask = SubTask.objects.filter(sub_task_id__startswith="ST_").aggregate(Max("sub_task_id"))["sub_task_id__max"]
                    if last_subtask:
                        try:
                            last_sequence = int(last_subtask.split("_")[1])
                        except (IndexError, ValueError):
                            last_sequence = 0
                    else:
                        last_sequence = 0

                    subtask_objects = []
                    for row in csv_rows:
                        try:
                            last_sequence += 1
                            new_sub_task_id = f"ST_{last_sequence:05d}"

                            subtask = SubTask(
                                task=task,
                                sub_task_id=new_sub_task_id,
                                address_line_1=row.get("Address 1", ""),
                                address_line_2=row.get("Address 2", ""),
                                contact_person_name=row.get("Contact Person’s Name", ""),
                                contact_person_number=row.get("Contact Person’s Number", ""),
                                latitude=row.get("Latitude") or None,
                                longitude=row.get("Longitude") or None,
                                unique_id=row.get("Unique ID", ""),
                                type_of_user=row.get("Type of User", "").upper() or None,
                                pincode=row.get("PINCODE", ""),
                                city=row.get("City", ""),
                                district=row.get("District", ""),
                                state=row.get("State", ""),
                                entity_type=row.get("Entity Type", "").upper() or None,
                                organisation_name=row.get("Merchant Name / Organisation Name", ""),
                                registered_mobile_number=row.get("Registered Mobile Number", ""),
                                otp_verified=True if str(row.get("Registered Mobile Number", "")).strip() else False,
                                verification_id=row.get("Verification ID", ""),
                                created_by=user,
                                modified_by=user,
                            )
                            subtask_objects.append(subtask)
                        except Exception as e:
                            print(f"Skipping row due to error: {e}")
                            continue

                    if subtask_objects:
                        SubTask.objects.bulk_create(subtask_objects)

                    # After subtasks are created, set cumulative_amount as subtasks * reward assigned to the task
                    task.refresh_from_db()
                    # Calculate cumulative_amount and total subtasks for all flows, fallback to old logic if no flows
                    task_flows = list(task.task_flow_entries.all())
                    subtasks = task.subtasks.all()
                    total_subtasks = subtasks.count()
                    cumulative_amount = 0
                    flow_reward_map = {tf.flow_id: tf.reward for tf in task_flows}
                    from tasks.models import SubTaskTracker
                    trackers = SubTaskTracker.objects.filter(subtask__task=task)
                    if task_flows:
                        # Multi-flow logic
                        if trackers.exists():
                            for tracker in trackers:
                                cumulative_amount += tracker.reward or flow_reward_map.get(tracker.flow_id, 0)
                        else:
                            cumulative_amount = sum([tf.reward for tf in task_flows]) * total_subtasks
                    else:
                        # No flows: fallback to old logic
                        # Try to get reward from request data or use 0
                        reward = 0
                        task_flow_entries = data.get('task_flow_entries', [])
                        if task_flow_entries and isinstance(task_flow_entries, list) and len(task_flow_entries) > 0:
                            reward = task_flow_entries[0].get('reward', 0)
                        elif hasattr(task, 'reward'):
                            reward = getattr(task, 'reward', 0)
                        cumulative_amount = total_subtasks * reward
                    task.cumulative_amount = cumulative_amount
                    task.save()

                # Refresh task to include latest TaskFlow and SubTask entries
                task.refresh_from_db()
                # Reload task with flows for serialization
                task = Task.objects.prefetch_related('task_flow_entries').get(id=task.id)
                response_serializer = TaskSerializer(task)
                return HttpResponse.Success({
                    "message": "Task created successfully with SubTasks (if provided)",
                    "task": response_serializer.data
                })

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def patch(self, request):
        try:
            task_id = request.GET.get("task_id", "")
            if not task_id:
                return HttpResponse.BadRequest("task_id is required!")

            task = Task.objects.get(id=task_id)

            if not can_access_task(request.user, task):
                return HttpResponse.BadRequest("You do not have permission to update this task.")

            data = request.data.copy()

            task_flow_entries = data.get("task_flow_entries")
            if task_flow_entries and isinstance(task_flow_entries, str):
                try:
                    data["task_flow_entries"] = json.loads(task_flow_entries)
                except json.JSONDecodeError:
                    return HttpResponse.BadRequest({"error": "Invalid JSON for task_flow_entries"})

            serializer = TaskSerializer(task, data=data, partial=True, context={"request": request})
            if serializer.is_valid():
                serializer.save(modified_by=request.user)
                return HttpResponse.Success({"task": serializer.data})
            return HttpResponse.BadRequest(serializer.errors)

        except Task.DoesNotExist:
            return HttpResponse.BadRequest("Task not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def delete(self, request):
        try:
            task_id = request.GET.get("task_id", "")
            if not task_id:
                return HttpResponse.BadRequest("task_id is required!")

            task = Task.objects.get(id=task_id)

            if not can_access_task(request.user, task):
                return HttpResponse.BadRequest("You do not have permission to delete this task.")

            task.delete()
            return HttpResponse.Success({"msg": "Task deleted successfully"})
        except Task.DoesNotExist:
            return HttpResponse.BadRequest("Task not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class TaskCloseView(APIView):
    permission_classes = []

    def post(self, request):
        try:
            task_id = request.data.get("task_id") or request.GET.get("task_id")
            if not task_id:
                return HttpResponse.BadRequest("task_id is required")
            task = Task.objects.get(id=task_id)

            if not can_access_task(request.user, task):
                return HttpResponse.BadRequest("You do not have permission to close this task.")

            force_val = request.data.get("force") if hasattr(request, "data") else None
            if force_val is None:
                force_val = request.GET.get("force")
            # Default to allowing closure unless explicitly disabled
            force = True
            if isinstance(force_val, bool):
                force = force_val
            elif isinstance(force_val, str):
                force = force_val.strip().lower() in {"true", "1", "yes", "y", "on"}

            pending_qs = SubTask.objects.filter(task=task).exclude(status=SUBTASK_STATUS.COMPLETED.value)
            pending = pending_qs.count()
            if pending > 0 and not force:
                return HttpResponse.BadRequest({"error": "All subtasks must be completed before closing", "pending_subtasks": pending})

            complete_remaining_val = request.data.get("complete_remaining") if hasattr(request, "data") else None
            if complete_remaining_val is None:
                complete_remaining_val = request.GET.get("complete_remaining")
            complete_remaining = False
            if isinstance(complete_remaining_val, bool):
                complete_remaining = complete_remaining_val
            elif isinstance(complete_remaining_val, str):
                complete_remaining = complete_remaining_val.strip().lower() in {"true", "1", "yes", "y", "on"}

            auto_completed = 0
            if force and complete_remaining and pending > 0:
                auto_completed = pending_qs.update(status=SUBTASK_STATUS.COMPLETED.value, modified_by=request.user)

            task.badge = TASK_STATUS.CLOSED.value
            task.status = TASK_STATUS.CLOSED.value
            # task.progress = 100
            # task.completed = True
            task.modified_by = request.user
            task.save()
            serializer = TaskSerializer(task, context={"request": request})
            return HttpResponse.Success({"message": "Task closed successfully", "task": serializer.data, "auto_completed_subtasks": auto_completed})
        except Task.DoesNotExist:
            return HttpResponse.BadRequest("Task not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
