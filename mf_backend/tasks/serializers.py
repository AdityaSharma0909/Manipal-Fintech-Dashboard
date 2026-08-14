import csv
import io
import json
from rest_framework import serializers
from .models import (
Task, TaskFlow, SubTask , SubTaskDocument, SubTaskTracker,
SubTaskApproval, APPROVAL_STATUS,
SubTaskApproval, StepCorrection, SubTaskTracker
)
from flows.serializers import FlowStepTrackerSerializer
from flows.models import Flow
from utils.constants import ROLES, FLOW_STATUS, FLOW_DOCUMENT_TYPE, DOCUMENT_FLOW
from collections import defaultdict


class TaskFlowSerializer(serializers.ModelSerializer):
    flow = serializers.PrimaryKeyRelatedField(queryset=Flow.objects.all())
    flow_description = serializers.CharField(source='flow.flow_description', read_only=True)
    status = serializers.SerializerMethodField()
    assigned = serializers.SerializerMethodField()
    completed_time = serializers.SerializerMethodField()
    assigned_usernames = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    assigned_count = serializers.SerializerMethodField()

    class Meta:
        model = TaskFlow
        fields = ('id', 'flow', 'flow_description', 'condition', 'reward', 'order', 'status', 'assigned', 'assigned_count', 'progress', 'completed_time', 'assigned_usernames')

    def get_assigned(self, obj):
        from tasks.models import SubTaskTracker, SubTask
        tracker_usernames = list(
            SubTaskTracker.objects
            .filter(subtask__task=obj.task, flow=obj.flow)
            .values_list("subtask__assign_to__username", flat=True)
        )
        subtask_usernames = list(
            SubTask.objects
            .filter(task=obj.task)
            .values_list("assign_to__username", flat=True)
        )
        merged = [u for u in tracker_usernames + subtask_usernames if u]
        seen = set()
        deduped = []
        for u in merged:
            if u not in seen:
                seen.add(u)
                deduped.append(u)
        return deduped
    
    def get_assigned_count(self, obj):
        from tasks.models import SubTaskTracker, SubTask
        count = SubTaskTracker.objects.filter(subtask__task=obj.task, flow=obj.flow).count()
        if count == 0:
            count = SubTask.objects.filter(task=obj.task, assign_to__isnull=False).count()
        return count

    def get_status(self, obj):
        from tasks.models import SubTaskTracker
        total = SubTaskTracker.objects.filter(subtask__task=obj.task, flow=obj.flow).count()
        completed = SubTaskTracker.objects.filter(subtask__task=obj.task, flow=obj.flow, progress=100).count()
        if total == 0:
            return "YET_TO_START"
        if completed == total and total > 0:
            return "COMPLETED"
        return "IN_PROGRESS"

    def get_progress(self, obj):
        from tasks.models import SubTaskTracker
        total = SubTaskTracker.objects.filter(subtask__task=obj.task, flow=obj.flow).count()
        if total == 0:
            return 0
        completed = SubTaskTracker.objects.filter(subtask__task=obj.task, flow=obj.flow, progress=100).count()
        return (completed * 100) // total

    def get_completed_time(self, obj):
        from tasks.models import SubTaskTracker
        last = (
            SubTaskTracker.objects
            .filter(subtask__task=obj.task, flow=obj.flow, progress=100)
            .order_by("-modified_at")
            .first()
        )
        return last.modified_at.isoformat() if last and getattr(last, "modified_at", None) else None
    
    def get_assigned_usernames(self, obj):
        from tasks.models import SubTaskTracker, SubTask
        tracker_usernames = list(
            SubTaskTracker.objects
            .filter(subtask__task=obj.task, flow=obj.flow)
            .values_list("subtask__assign_to__username", flat=True)
        )
        subtask_usernames = list(
            SubTask.objects
            .filter(task=obj.task)
            .values_list("assign_to__username", flat=True)
        )
        merged = [u for u in tracker_usernames + subtask_usernames if u]
        seen = set()
        deduped = []
        for u in merged:
            if u not in seen:
                seen.add(u)
                deduped.append(u)
        return deduped

class SubTaskSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    assign_to = serializers.SerializerMethodField()
    completed_at = serializers.SerializerMethodField()
    task_completed_timestamp = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = SubTask
        fields = "__all__"
        read_only_fields = ('created_at', 'modified_at')

    def get_status(self, obj):
        if not obj.status:
            return "NEW_TASK"
        return obj.status

    def get_assign_to(self, obj):
        user = obj.assign_to
        if user:
            return {
                "user_id": str(user.user_id),
                "employee_id": user.employee_id,
                "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip()
            }
        return None
    
    def get_completed_at(self, obj):
        from tasks.models import SubTaskTracker
        trackers = (
            SubTaskTracker.objects
            .filter(subtask=obj)
            .order_by("-modified_at")
        )
        for t in trackers:
            status = t.flow_status
            if status in {
                "LOCATION_VERIFICATION_VERIFIED_BY_CENTRAL_OPS",
                "LOCATION_RE_VERIFICATION_VERIFIED_BY_CENTRAL_OPS",
                "UPLOAD_KYC_DOCUMENT_VERIFIED_BY_CENTRAL_OPS",
                "LEAD_GENERATION_COMPLETED",
                "LEAD_CLOSURE_COMPLETED",
                "VERIFIED_BY_CENTRAL_OPS",
            }:
                return t.step_timestamps.get("TASK_COMPLETED") or t.modified_at.isoformat()
        return None
    
    def get_task_completed_timestamp(self, obj):
        # Explicitly return the TASK_COMPLETED timestamp string if available
        from tasks.models import SubTaskTracker
        if getattr(obj, "status", None) != "COMPLETED":
            return None
        tracker = (
            SubTaskTracker.objects
            .filter(subtask=obj)
            .order_by("-modified_at")
            .first()
        )
        if not tracker:
            return None
        return tracker.step_timestamps.get("TASK_COMPLETED")


class TaskSerializer(serializers.ModelSerializer):
    task_flow_entries = TaskFlowSerializer(many=True, required=False)
    subtasks = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            'id', 'task_id', 'task_summary', 'is_auto_reject', 'auto_reject_time',
            'total_reward_assigned', 'priority', 'upload_customer_data', 'upload_employee_file',
            'state', 'district', 'city', 'team', 'badge', 'cumulative_amount',
            'status', 'progress', 'assigned_by', 'completed',
            'created_at', 'modified_at', 'created_by', 'modified_by',
            'task_flow_entries', 'subtasks'
        )
        read_only_fields = ('created_at', 'modified_at')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
        except Exception:
            User = None
        def _username_from_id(val):
            if not val or not User:
                return None if not val else val
            user_obj = User.objects.filter(pk=val).first()
            return getattr(user_obj, "username", None) if user_obj else val
        representation["assigned_by"] = _username_from_id(representation.get("assigned_by"))
        return representation

    def validate_progress(self, value):
        if value is None:
            return value
        if not isinstance(value, int):
            raise serializers.ValidationError("progress must be an integer between 0 and 100")
        if value < 0 or value > 100:
            raise serializers.ValidationError("progress must be between 0 and 100")
        return value

    def to_internal_value(self, data):
        """
        Handle task_flow_entries when sent as JSON string (e.g. multipart/form-data).
        """
        if isinstance(data.get('task_flow_entries'), str):
            try:
                parsed = json.loads(data.get('task_flow_entries'))
                data = data.copy()
                data.setlist('task_flow_entries', [parsed] if not isinstance(parsed, list) else parsed)
            except json.JSONDecodeError:
                pass
        return super().to_internal_value(data)

    def get_subtasks(self, obj):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        subtasks = obj.subtasks.all()
        if user and hasattr(user, "role") and user.role == ROLES.AGENT.value:
            subtasks = subtasks.filter(assign_to=user)

        return SubTaskSerializer(subtasks, many=True).data

    def create(self, validated_data):
        task_flow_data = validated_data.pop('task_flow_entries', [])
        upload_file = validated_data.get('upload_customer_data', None)
        task = Task.objects.create(**validated_data)

        # If no task_flow_entries provided, create a default one
        # Remove default TaskFlow creation
        # TaskFlow should be created in the view, not here

        # If there's an uploaded CSV of customers, parse and create subtasks
        if upload_file:
            self._create_subtasks_from_csv(task, upload_file)

        # Calculate cumulative_amount: sum of all TaskFlow rewards for each subtask
        # It should be calculated in the view after TaskFlow and SubTask creation
        return task

    def update(self, instance, validated_data):
        task_flow_data = validated_data.pop('task_flow_entries', None)
        upload_file = validated_data.get('upload_customer_data', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Remove TaskFlow creation from serializer
        # TaskFlow should be created in the view, not here

        if upload_file:
            self._create_subtasks_from_csv(instance, upload_file)

        return instance

    def _create_subtasks_from_csv(self, task, upload_file):
        """
        Parse uploaded CSV and create SubTask records.
        Expected columns: customer_id, contact_name, organization_name, contact_no, address, assign_to
        """
        try:
            file_data = upload_file.read().decode('utf-8')
        except AttributeError:
            file_data = upload_file.read().decode('utf-8')

        reader = csv.DictReader(io.StringIO(file_data))
        created = 0
        
        from django.db.models import Max
        last_subtask = SubTask.objects.filter(sub_task_id__startswith="ST_").aggregate(Max("sub_task_id"))["sub_task_id__max"]
        if last_subtask:
            try:
                last_sequence = int(last_subtask.split("_")[1])
            except (IndexError, ValueError):
                last_sequence = 0
        else:
            last_sequence = 0

        for row in reader:
            last_sequence += 1
            new_sub_task_id = f"ST_{last_sequence:05d}"
            
            customer_id = row.get('customer_id') or row.get('customerId') or row.get('id') or ''
            contact_name = row.get('contact_name') or row.get('contactName') or row.get('name') or ''
            organization_name = row.get('organization_name') or row.get('organizationName') or ''
            contact_no = row.get('contact_no') or row.get('contactNo') or ''
            address = row.get('address') or ''
            assign_to = None
            assign_to_val = row.get('assign_to') or row.get('assignTo') or ''

            if assign_to_val:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user_qs = User.objects.filter(id=assign_to_val)
                if not user_qs.exists():
                    user_qs = User.objects.filter(username=assign_to_val)
                if not user_qs.exists():
                    user_qs = User.objects.filter(email=assign_to_val)
                assign_to = user_qs.first() if user_qs.exists() else None
                if not assign_to:
                    print(f"[CSV SubTask Assignment] No user found for assign_to value: '{assign_to_val}'")

            SubTask.objects.create(
                task=task,
                sub_task_id=new_sub_task_id,
                customer_id=customer_id,
                contact_name=contact_name,
                organization_name=organization_name,
                contact_no=contact_no,
                address=address,
                assign_to=assign_to,
                created_by=task.created_by
            )
            created += 1
        return created


class TaskMiniSerializer(serializers.ModelSerializer):
    flows = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'total_reward_assigned', 'priority', 'flows']

    def get_flows(self, obj):
    # Get the current subtask from context
        current_subtask = self.context.get('current_subtask')
        
        
        
        if not current_subtask:
            
            return []
        
        # Filter trackers by the CURRENT subtask only
        trackers = SubTaskTracker.objects.filter(
            subtask=current_subtask
        ).select_related("flow")
        

        
        taskflows = TaskFlow.objects.filter(task=obj).select_related("flow")
        

        flow_rewards = {tf.flow.id: tf.reward for tf in taskflows}
        flow_progress_map = defaultdict(list)
        
        for tracker in trackers:
            flow_progress_map[tracker.flow.id].append(tracker.progress)

        seen = set()
        result = []

        # Include flows from trackers (specific to this subtask)
        for tracker in trackers:
            flow_id = tracker.flow.id
            if flow_id not in seen:
                seen.add(flow_id)
                progress_list = flow_progress_map.get(flow_id, [])
                progress = sum(progress_list) // len(progress_list) if progress_list else 0
                reward = tracker.reward or flow_rewards.get(flow_id, 0)
                result.append({
                    "flow_id": flow_id,
                    "flow_description": tracker.flow.flow_description,
                    "subtask_tracker_id": tracker.id,
                    "reward": reward,
                    "progress": progress
                })

        # Include remaining taskflows not yet mapped to this subtask
        for tf in taskflows:
            flow_id = tf.flow.id
            if flow_id not in seen:
                seen.add(flow_id)
                result.append({
                    "flow_id": flow_id,
                    "flow_description": tf.flow.flow_description,
                    "subtask_tracker_id": "",
                    "reward": tf.reward,
                    "progress": 0
                })

        
        return result


class GetSubTaskSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    id = serializers.UUIDField(required=False)
    assign_to = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = SubTask
        fields = "__all__"
        extra_fields = ['category']
        read_only_fields = ('created_at', 'modified_at')

    def get_status(self, obj):
        if not obj.status:
            return "NEW_TASK"
        return obj.status

    def get_assign_to(self, obj):
        user = obj.assign_to
        if user:
            return {
                "user_id": str(user.user_id),
                "employee_id": user.employee_id,
                "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip()
            }
        return None
    
    def get_task(self, obj):
        return TaskMiniSerializer(obj.task, context={'current_subtask': obj}).data

    def get_category(self, obj):
        # Default: Approval
        from tasks.models import SubTaskTracker, SubTaskApproval, StepCorrection
        trackers = SubTaskTracker.objects.filter(subtask=obj)
        # Completed
        if getattr(obj, "status", None) == "COMPLETED":
            return "completed"
        # Rejected
        if trackers.filter(central_ops_status="REJECTED").exists():
            return "rejected"
        # Correction - Check for pending corrections in any tracker's approval steps
        if SubTaskApproval.objects.filter(
            subtask_tracker__in=trackers,
            corrections__status=StepCorrection.CorrectionStatus.PENDING_CORRECTION
        ).exists():
            return "correction"
        # Approval
        return "approval"
    
   


class SubTaskTrackerSerializer(serializers.ModelSerializer):
    flow_steps = serializers.SerializerMethodField()

    class Meta:
        model = SubTaskTracker
        fields = "__all__"
        read_only_fields = ('created_at', 'modified_at')

    def get_flow_steps(self, obj):
        if obj.flow:
            steps = obj.flow.flow_steps.all().order_by('step_order')
            return FlowStepTrackerSerializer(steps, many=True).data
        return []
    
class SubTaskTrackerGetSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    flow_steps = serializers.SerializerMethodField()
    flow = serializers.SerializerMethodField()
    all_documents = serializers.SerializerMethodField() 

    step_approvals = serializers.SerializerMethodField()
    current_review_step = serializers.IntegerField(read_only=True)
    all_steps_approved = serializers.BooleanField(read_only=True)
    has_pending_corrections = serializers.SerializerMethodField()
    pending_corrections_list = serializers.SerializerMethodField()

    
    def get_all_documents(self, obj):
        """
        Returns ALL documents uploaded for this subtask
        in ONE flat list (independent of flow_steps)
        """
        documents = obj.subtask.subtask_document.all().select_related()

        return SubTaskDocumentSerializer(
            documents,
            many=True,
            context={"tracker": obj}
        ).data

    class Meta:
        model = SubTaskTracker
        fields = "__all__"
        extra_fields = ['category']

    def get_category(self, obj):
        # Completed
        total_steps = obj.step_approvals.count()
        approved_steps = obj.step_approvals.filter(approval_status="APPROVED").count()
        if total_steps > 0 and total_steps == approved_steps:
            return "completed"
        # Rejected
        if obj.central_ops_status == "REJECTED":
            return "rejected"
        # Correction
        if obj.step_approvals.filter(
            approval_status=SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
        ).exists():
            return "correction"
        # Approval
        if obj.step_approvals.filter(approval_status="SUBMITTED").exists():
            return "approval"
        return "approval"

    def get_flow_steps(self, obj):
        """Enrich flow steps with completion status, timestamps, and documents"""
        if not obj.flow:
            return []
        
        steps = obj.flow.flow_steps.all().order_by('step_order')
        flow_desc = obj.flow.flow_description
        
        enriched_steps = []
        
        for step in steps:
            step_data = {
                "step_order": step.step_order,
                "step_description": step.step_description,
                "is_completed": False,
                "completed_at": None,
                "documents": [],
                "verification_details": {}
            }
            
            # === UPLOAD KYC DOCUMENT FLOW ===
            if flow_desc == "Upload KYC Document":
                if step.step_order == 1:  # Visit merchant
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.UPLOAD_KYC_DOCUMENTS_STARTED.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("REACHED_ADDRESS")
                    
                elif step.step_order == 2:  # Upload photos/scans (PAN, Aadhaar, Other docs)
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.UPLOAD_KYC_DOCUMENTS_STARTED.value,
                        FLOW_STATUS.KYC_REACHED_ADDRESS.value,
                        FLOW_STATUS.PAN_CARD_VERIFIED.value,
                        FLOW_STATUS.AADHAR_CARD_VERIFIED.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("OTHER_DOCUMENTS_VERIFIED")
                    step_data["verification_details"] = {
                        "pan_verified": obj.is_pan_verify,
                        "pan_number": obj.pan_number,
                        "aadhar_verified": obj.is_aadhar_verify,
                        "aadhar_number": obj.aadhar_number,
                        "other_document_verified": obj.other_document_verified,
                        "other_document_type": obj.other_document
                    }
                    # Get ALL documents (PAN + Aadhaar + Other)
                    doc_types = [
                        FLOW_DOCUMENT_TYPE.PAN_CARD.value,
                        FLOW_DOCUMENT_TYPE.FRONT_AADHAR_CARD.value,
                        FLOW_DOCUMENT_TYPE.BACK_AADHAR_CARD.value,
                        FLOW_DOCUMENT_TYPE.FRONT_DRIVING_LICENSE.value,
                        FLOW_DOCUMENT_TYPE.BACK_DRIVING_LICENSE.value,
                        FLOW_DOCUMENT_TYPE.FRONT_PASSPORT.value,
                        FLOW_DOCUMENT_TYPE.BACK_PASSPORT.value,
                        FLOW_DOCUMENT_TYPE.FRONT_VOTER_ID.value,
                        FLOW_DOCUMENT_TYPE.BACK_VOTER_ID.value
                    ]
                    docs = obj.subtask.subtask_document.filter(
                        document_type__in=doc_types,
                        document_flow=DOCUMENT_FLOW.KYC_DOCUMENT_UPLOAD.value
                    )
                    step_data["documents"] = SubTaskDocumentSerializer(docs, many=True).data
                    
                elif step.step_order == 3:  # Fill KYC form fields
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.UPLOAD_KYC_DOCUMENTS_STARTED.value,
                        FLOW_STATUS.KYC_REACHED_ADDRESS.value,
                        FLOW_STATUS.PAN_CARD_VERIFIED.value,
                        FLOW_STATUS.AADHAR_CARD_VERIFIED.value,
                        FLOW_STATUS.OTHER_DOCUMENTS_VERIFIED.value,
                        FLOW_STATUS.CUSTOMER_DETAILS_ADDED.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("CUSTOMER_ADDRESS_ADDED")
                    step_data["verification_details"] = {
                        "phone_verified": obj.is_phone_verified,
                        "full_name": obj.full_name,
                        "date_of_birth": str(obj.date_of_birth) if obj.date_of_birth else None,
                        "gender": obj.gender,
                        "father_name": obj.father_name,
                        "email": obj.email,
                        "phone_number": obj.phone_number,
                        "whatsapp_number": obj.whatsapp_number,
                        "profession": obj.profession,
                        "permanent_address": obj.permanent_address,
                        "permanent_address_pincode": obj.permanent_address_pincode,
                        "permanent_address_state": obj.permanent_address_state,
                        "permanent_address_city": obj.permanent_address_city,
                        "permanent_address_district": obj.permanent_address_district,
                        "current_address": obj.current_address,
                        "current_address_pincode": obj.current_address_pincode,
                        "current_address_state": obj.current_address_state,
                        "current_address_city": obj.current_address_city,
                        "current_address_district": obj.current_address_district
                    }
                    # Get profile pic
                    profile_docs = obj.subtask.subtask_document.filter(
                        document_type=FLOW_DOCUMENT_TYPE.PROFILE_PIC.value,
                        document_flow=DOCUMENT_FLOW.KYC_DOCUMENT_UPLOAD.value
                    )
                    step_data["documents"] = SubTaskDocumentSerializer(profile_docs, many=True).data
                    
                elif step.step_order == 4:  # Ops team verification
                    step_data["is_completed"] = obj.flow_status == FLOW_STATUS.VERIFIED_BY_CENTRAL_OPS.value or obj.progress == 100
                    step_data["completed_at"] = obj.step_timestamps.get("VERIFICATION_BY_OPS")
                    step_data["verification_details"] = {
                        "central_ops_status": obj.central_ops_status,
                        "central_ops_remarks": obj.central_ops_remarks,
                        "verified_by": obj.central_ops_user.username if obj.central_ops_user else None
                    }

            # === LOCATION VERIFICATION FLOW ===
            elif flow_desc == "Location Verification":
                if step.step_order == 1:  # Reach address
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.LOCATION_VERIFICATION_STARTED.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("REACHED_ADDRESS")
                    
                elif step.step_order == 2:  # Upload location photo
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.LOCATION_VERIFICATION_STARTED.value,
                        FLOW_STATUS.LOCATION_VERIFICATION_REACHED_ADDRESS.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("LOCATION_PHOTO_ADDED")
                    location_docs = obj.subtask.subtask_document.filter(
                        document_type=FLOW_DOCUMENT_TYPE.LOCATION_PHOTO.value
                    )
                    step_data["documents"] = SubTaskDocumentSerializer(location_docs, many=True).data
                    
                elif step.step_order == 3:  # Upload selfie
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.LOCATION_VERIFICATION_STARTED.value,
                        FLOW_STATUS.LOCATION_VERIFICATION_REACHED_ADDRESS.value,
                        FLOW_STATUS.LOCATION_PHOTO_ADDED.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("SELFIE_PHOTO_ADDED")
                    selfie_docs = obj.subtask.subtask_document.filter(
                        document_type=FLOW_DOCUMENT_TYPE.SELFIE_PHOTO.value
                    )
                    step_data["documents"] = SubTaskDocumentSerializer(selfie_docs, many=True).data
                    
                elif step.step_order == 4:  # Ops verification
                    step_data["is_completed"] = obj.flow_status == FLOW_STATUS.VERIFIED_BY_CENTRAL_OPS.value or obj.progress == 100
                    step_data["completed_at"] = obj.step_timestamps.get("VERIFICATION_BY_OPS")
                    step_data["verification_details"] = {
                        "central_ops_status": obj.central_ops_status,
                        "central_ops_remarks": obj.central_ops_remarks,
                        "verified_by": obj.central_ops_user.username if obj.central_ops_user else None
                    }
            
            # === LOCATION RE-VERIFICATION FLOW ===
            elif flow_desc == "Location Re-Verification":
                if step.step_order == 1:  # Reach address
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.LOCATION_RE_VERIFICATION_STARTED.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("REACHED_ADDRESS")
                    
                elif step.step_order == 2:  # Upload location photo
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.LOCATION_RE_VERIFICATION_STARTED.value,
                        FLOW_STATUS.LOCATION_RE_VERIFICATION_REACHED_ADDRESS.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("LOCATION_PHOTO_ADDED")
                    location_docs = obj.subtask.subtask_document.filter(
                        document_type=FLOW_DOCUMENT_TYPE.LOCATION_PHOTO.value,
                        document_flow=DOCUMENT_FLOW.LOCATION_REVERIFICATION.value
                    )
                    step_data["documents"] = SubTaskDocumentSerializer(location_docs, many=True).data
                    
                elif step.step_order == 3:  # Upload selfie
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.LOCATION_RE_VERIFICATION_STARTED.value,
                        FLOW_STATUS.LOCATION_RE_VERIFICATION_REACHED_ADDRESS.value,
                        FLOW_STATUS.LOCATION_PHOTO_ADDED.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("SELFIE_PHOTO_ADDED")
                    selfie_docs = obj.subtask.subtask_document.filter(
                        document_type=FLOW_DOCUMENT_TYPE.SELFIE_PHOTO.value,
                        document_flow=DOCUMENT_FLOW.LOCATION_REVERIFICATION.value
                    )
                    step_data["documents"] = SubTaskDocumentSerializer(selfie_docs, many=True).data
                    
                elif step.step_order == 4:  # Ops verification
                    step_data["is_completed"] = obj.flow_status == FLOW_STATUS.VERIFIED_BY_CENTRAL_OPS.value or obj.progress == 100
                    step_data["completed_at"] = obj.step_timestamps.get("VERIFICATION_BY_OPS")
                    step_data["verification_details"] = {
                        "central_ops_status": obj.central_ops_status,
                        "central_ops_remarks": obj.central_ops_remarks,
                        "verified_by": obj.central_ops_user.username if obj.central_ops_user else None
                    }
            
            # === LEAD GENERATION FLOW ===
            elif flow_desc == "Lead Generation":
                if step.step_order == 1:  # Add lead details
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.LEAD_GENERATION_STARTED.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("ADD_LEAD_DETAILS")
                    step_data["verification_details"] = {
                        "full_name": obj.full_name,
                        "phone_number": obj.phone_number,
                        "pincode": obj.current_address_pincode,
                        "state": obj.current_address_state,
                        "district": obj.current_address_district,
                        "product_category": obj.product_category,
                        "product_sub_category": obj.product_sub_category,
                        "amount": str(obj.amount) if obj.amount else None
                    }
                    
                elif step.step_order == 2:  # OTP verification
                    step_data["is_completed"] = obj.flow_status == FLOW_STATUS.LEAD_OTP_VERIFIED.value or obj.progress == 100
                    step_data["completed_at"] = obj.step_timestamps.get("LEAD_OTP_VERIFIED")
                    step_data["verification_details"] = {
                        "phone_verified": obj.is_phone_verified
                    }
                elif step.step_order == 3:  # Mark Complete in app
                    step_data["is_completed"] = obj.flow_status == FLOW_STATUS.LEAD_GENERATION_COMPLETED.value or obj.progress == 100
                    step_data["completed_at"] = obj.step_timestamps.get("TASK_COMPLETED")
                    step_data["verification_details"] = {}

            elif flow_desc == "Lead Closure":
                if step.step_order == 1:
                    step_data["is_completed"] = obj.flow_status not in [
                        FLOW_STATUS.LEAD_CLOSURE_STARTED.value
                    ]
                    step_data["completed_at"] = obj.step_timestamps.get("LEAD_CLOSURE_DETAILS_ADDED")
                    step_data["verification_details"] = {
                        "customer_id": obj.customer_id,
                        "full_name": obj.full_name,
                        "amount": str(obj.amount) if obj.amount else None,
                        "loan_date": str(obj.loan_date) if obj.loan_date else None,
                        "loan_account_number": obj.loan_account_number,
                        "product_category": obj.product_category,
                        "product_sub_category": obj.product_sub_category,
                        "bank_name": obj.bank_name,
                        "lead_type": obj.lead_type
                    }
                    pledge_docs = obj.subtask.subtask_document.filter(
                        document_type=FLOW_DOCUMENT_TYPE.PLEDGE_CARD_KFS.value,
                        document_flow=DOCUMENT_FLOW.LEAD_CLOSURE.value
                    )
                    step_data["documents"] = SubTaskDocumentSerializer(pledge_docs, many=True).data

                elif step.step_order == 2:
                    step_data["is_completed"] = obj.flow_status == FLOW_STATUS.LEAD_CLOSURE_COMPLETED.value or obj.progress == 100
                    step_data["completed_at"] = obj.step_timestamps.get("LEAD_CLOSURE_COMPLETED")
            
            enriched_steps.append(step_data)
        
        return enriched_steps
    
    def get_flow(self, obj):
        if not obj.flow:
            return None
        return {
            "id": obj.flow.id,
            "flow_description": obj.flow.flow_description
        }
        
    def get_step_approvals(self, obj):
        """
        Only used in detail view (when id is passed).
        For list view, view will NOT request these.
        """
        # Prefetch friendly: ensure view uses prefetch_related if needed
        approvals = obj.step_approvals.all().order_by("step_order")
        return FlowStepApprovalSerializer(approvals, many=True).data

    def get_has_pending_corrections(self, obj):
        return obj.step_approvals.filter(
            approval_status=SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
        ).exists()

    def get_pending_corrections_list(self, obj):
        return list(
            obj.step_approvals.filter(
                approval_status=SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
            ).values_list("step_order", flat=True)
        )


class SubTaskDocumentSerializer(serializers.ModelSerializer):
    step_order = serializers.SerializerMethodField()
    class Meta:
        model = SubTaskDocument
        fields = ['step_order','document_id', 'document_flow', 'document_type', 'file_name', 'file']
    def get_step_order(self, obj):
        doc_type = obj.document_type
        doc_flow = obj.document_flow

        # ===== LOCATION VERIFICATION =====
        if doc_flow == DOCUMENT_FLOW.LOCATION_VERIFICATION.value:
            if doc_type == FLOW_DOCUMENT_TYPE.LOCATION_PHOTO.value:
                return 2
            if doc_type == FLOW_DOCUMENT_TYPE.SELFIE_PHOTO.value:
                return 3

        # ===== LOCATION RE-VERIFICATION =====
        if doc_flow == DOCUMENT_FLOW.LOCATION_REVERIFICATION.value:
            if doc_type == FLOW_DOCUMENT_TYPE.LOCATION_PHOTO.value:
                return 2
            if doc_type == FLOW_DOCUMENT_TYPE.SELFIE_PHOTO.value:
                return 3

        # ===== KYC DOCUMENT UPLOAD =====
        if doc_flow == DOCUMENT_FLOW.KYC_DOCUMENT_UPLOAD.value:
            if doc_type in [
                FLOW_DOCUMENT_TYPE.PAN_CARD.value,
                FLOW_DOCUMENT_TYPE.FRONT_AADHAR_CARD.value,
                FLOW_DOCUMENT_TYPE.BACK_AADHAR_CARD.value,
                FLOW_DOCUMENT_TYPE.FRONT_DRIVING_LICENSE.value,
                FLOW_DOCUMENT_TYPE.BACK_DRIVING_LICENSE.value,
                FLOW_DOCUMENT_TYPE.FRONT_PASSPORT.value,
                FLOW_DOCUMENT_TYPE.BACK_PASSPORT.value,
                FLOW_DOCUMENT_TYPE.FRONT_VOTER_ID.value,
                FLOW_DOCUMENT_TYPE.BACK_VOTER_ID.value,
            ]:
                return 2

        if doc_flow == DOCUMENT_FLOW.LEAD_CLOSURE.value:
            if doc_type == FLOW_DOCUMENT_TYPE.PLEDGE_CARD_KFS.value:
                return 1

            if doc_type == FLOW_DOCUMENT_TYPE.PROFILE_PIC.value:
                return 3

        # ===== LEAD GENERATION =====
        return None




class SubTaskTrackerDetailSerializer(serializers.ModelSerializer):
    flow_info = serializers.SerializerMethodField()
    flow_steps = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    class Meta:
        model = SubTaskTracker
        fields = [
            'id', 'flow_status', 'progress',
            'subtask', 'flow', 'flow_info', 'flow_steps','step_timestamps', 'documents',
            'created_at', 'modified_at', 'created_by', 'modified_by','step_number'
        ]

    def get_flow_info(self, obj):
        return {
            "id": obj.flow.id,
            "flow_description": obj.flow.flow_description
        }

    def get_flow_steps(self, obj):
        steps = obj.flow.flow_steps.all().order_by('step_order')
        return FlowStepTrackerSerializer(steps, many=True).data

    def get_documents(self, obj):
        docs = obj.subtask.subtask_document.all()
        return SubTaskDocumentSerializer(docs, many=True).data
    
    
class StepCorrectionSerializer(serializers.ModelSerializer):
    """Serializer for step correction details"""
    
    corrected_by_name = serializers.CharField(source='corrected_by.get_full_name', read_only=True)
    corrected_by_user_id = serializers.CharField(source='corrected_by.user_id', read_only=True)
    
    class Meta:
        model = StepCorrection
        fields = [
            'id', 'reason', 'comment', 'corrected_by', 'corrected_by_name',
            'corrected_by_user_id', 'corrected_at', 'status', 
            'resubmitted_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'corrected_at', 'resubmitted_at', 'resolved_at']


class FlowStepApprovalSerializer(serializers.ModelSerializer):
    """Serializer for flow step approval status"""
    
    step_description = serializers.CharField(source='flow_step.step_description', read_only=True)
    latest_correction = serializers.SerializerMethodField()
    correction_count = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = SubTaskApproval
        fields = [
            'id', 'step_order', 'step_description', 'approval_status',
            'latest_correction', 'correction_count', 'can_edit',
            'approved_by', 'approved_by_name', 'approved_at', 'updated_at'
        ]
        read_only_fields = ['id', 'step_order', 'step_description']
    
    def get_latest_correction(self, obj):
        """Get the most recent correction if any"""
        if obj.approval_status == SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED:
            latest = obj.corrections.filter(
                status=StepCorrection.CorrectionStatus.PENDING_CORRECTION
            ).first()
            if latest:
                return StepCorrectionSerializer(latest).data
        return None
    
    def get_correction_count(self, obj):
        """Get total number of corrections for this step"""
        return obj.corrections.count()
    
    def get_can_edit(self, obj):
        """Determine if field agent can edit this step"""
        return obj.approval_status == SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED


class SubTaskTrackerApprovalDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for subtask tracker with approval info"""
    
    step_approvals = FlowStepApprovalSerializer(many=True, read_only=True)
    flow_description = serializers.CharField(source='flow.flow_description', read_only=True)
    flow_id = serializers.CharField(source='flow.flow_id', read_only=True)
    has_pending_corrections = serializers.SerializerMethodField()
    pending_corrections_list = serializers.SerializerMethodField()
    
    class Meta:
        model = SubTaskTracker
        fields = [
            'id', 'flow_id', 'flow_description', 'flow_status', 'progress',
            'current_review_step', 'all_steps_approved', 'step_approvals',
            'has_pending_corrections', 'pending_corrections_list',
            'central_ops_status', 'central_ops_remarks', 'reward',
            'created_at', 'modified_at'
        ]
    
    def get_has_pending_corrections(self, obj):
        """Check if there are any pending corrections"""
        return obj.step_approvals.filter(
            approval_status=SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
        ).exists()
    
    def get_pending_corrections_list(self, obj):
        """Get list of step orders that need correction"""
        return list(
            obj.step_approvals.filter(
                approval_status=SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
            ).values_list('step_order', flat=True)
        )


class CentralOpsReviewSerializer(serializers.Serializer):
    """Serializer for Central Ops review action"""
    
    ACTION_CHOICES = [
        ('REVIEW', 'Mark as Reviewed'),
        ('SEND_BACK', 'Send Back for Correction'),
    ]
    
    tracker_id = serializers.UUIDField(required=True)
    step_order = serializers.IntegerField(required=True, min_value=1)
    action = serializers.ChoiceField(choices=ACTION_CHOICES, required=True)
    correction_reason = serializers.CharField(required=False, allow_blank=True)
    correction_comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate(self, data):
        """Validate that correction fields are provided when sending back"""
        if data['action'] == 'SEND_BACK':
            if not data.get('correction_reason'):
                raise serializers.ValidationError({
                    'correction_reason': 'Correction reason is required when sending back'
                })
        return data

class FinalApprovalSerializer(serializers.Serializer):
    ACTION_CHOICES = [
        ('APPROVE', 'Approve'),
        ('REJECT', 'Reject'),
        ('PARTIAL_APPROVE', 'Partial Approve'),
    ]

    tracker_id = serializers.UUIDField(required=True)
    action = serializers.ChoiceField(choices=ACTION_CHOICES, required=True)
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, data):
        if data['action'] in ['REJECT', 'PARTIAL_APPROVE'] and not data.get('comment'):
            raise serializers.ValidationError({
                'comment': 'Comment is required for reject or partial approval'
            })
        return data
