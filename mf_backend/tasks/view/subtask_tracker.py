from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from tasks.models import SubTask, SubTaskTracker, SubTaskDocument,SubTaskApproval, TaskFlow
from flows.models import Flow
from tasks.serializers import SubTaskTrackerSerializer, SubTaskTrackerDetailSerializer, SubTaskTrackerGetSerializer
from users.models import UserReward, User
from utils.responseHandler import HttpResponse
import traceback
from django.db import transaction
import traceback
from utils.constants import CENTRAL_OPS_STATUS, ROLES , SUBTASK_STATUS, FLOW_STATUS,  DOCUMENT_FLOW, FLOW_DOCUMENT_TYPE , OTHER_DOCUMENTS, TASK_STATUS
from tasks.utils import get_ist_time_str , is_otp_valid, generate_otp , to_bool
from django.utils import timezone
from django.db.models import Count, Q, F, Max
from datetime import datetime
import re
from onboarding_v2.helpers.lead_application_helpers import prepare_lead_create_data, create_lead
from onboarding_v2.constants import ApplicationStatus, LeadStatus
from onboarding_v2.models import LeadV2
from utils.envSetup import environment
from utils.sms import SMSService


def _should_initialize_approval(tracker):
    """
    Check if approval flow should be initialized.
    Triggers when field agent completes last step before ops approval.
    """
    return tracker.flow_status in [
        FLOW_STATUS.SELFIE_PHOTO_ADDED.value,  # Location Verification - step 3
        FLOW_STATUS.CUSTOMER_ADDRESS_ADDED.value,  # Upload KYC Document - step 3
        FLOW_STATUS.ADD_LEAD_DETAILS.value,  # Lead Generation - step 1
    ]


def _get_step_number_from_status(tracker):
    """
    Calculate NEXT step number to be completed based on flow status.
    Returns current step + 1, capped at total flow steps when complete.
    """
    flow_desc = tracker.flow.flow_description
    status = tracker.flow_status
    
    # Get total field agent steps for this flow
    total_steps_map = {
        "Location Verification": 4,
        "Location Re-Verification": 7,
        "Upload KYC Document": 4,
        "Lead Generation": 3,
        "Lead Closure": 2,
    }
    total_steps = total_steps_map.get(flow_desc, 4)
    
    # Location Verification
    if flow_desc == "Location Verification":
        STATUS_TO_CURRENT_STEP = {
            FLOW_STATUS.LOCATION_VERIFICATION_STARTED.value: 0,
            FLOW_STATUS.LOCATION_VERIFICATION_REACHED_ADDRESS.value: 1,
            FLOW_STATUS.LOCATION_PHOTO_ADDED.value: 2,
            FLOW_STATUS.SELFIE_PHOTO_ADDED.value: 3,
            FLOW_STATUS.SENT_TO_CENTRAL_OPS.value: 3,
            FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value: 3,
            FLOW_STATUS.LOCATION_VERIFICATION_VERIFIED_BY_CENTRAL_OPS.value: 4,
        }
        current_step = STATUS_TO_CURRENT_STEP.get(status, 0)
        
        if status == FLOW_STATUS.LOCATION_VERIFICATION_VERIFIED_BY_CENTRAL_OPS.value:
            return 4
        else:
            return min(current_step + 1, total_steps)
    
    # Location Re-Verification
    elif flow_desc == "Location Re-Verification":
        STATUS_TO_CURRENT_STEP = {
            FLOW_STATUS.LOCATION_RE_VERIFICATION_STARTED.value: 0,
            FLOW_STATUS.LOCATION_RE_VERIFICATION_REACHED_ADDRESS.value: 1,
            FLOW_STATUS.LOCATION_PHOTO_ADDED.value: 2,
            FLOW_STATUS.SELFIE_PHOTO_ADDED.value: 3,
            FLOW_STATUS.SENT_TO_CENTRAL_OPS.value: 3,
            FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value: 3,
            FLOW_STATUS.LOCATION_RE_VERIFICATION_VERIFIED_BY_CENTRAL_OPS.value: 7,
        }
        current_step = STATUS_TO_CURRENT_STEP.get(status, 0)
        
        if status == FLOW_STATUS.LOCATION_RE_VERIFICATION_VERIFIED_BY_CENTRAL_OPS.value:
            return 7
        else:
            return min(current_step + 1, total_steps)
    
    # Upload KYC Document
    elif flow_desc == "Upload KYC Document":
        STATUS_TO_CURRENT_STEP = {
            FLOW_STATUS.UPLOAD_KYC_DOCUMENTS_STARTED.value: 0,
            FLOW_STATUS.KYC_REACHED_ADDRESS.value: 1,  # Step 1 done
            FLOW_STATUS.DOCUMENTS_VERIFIED.value: 2,  # Step 2 done (all docs verified)
            FLOW_STATUS.CUSTOMER_DETAILS_ADDED.value: 3,  # Step 3 done
            FLOW_STATUS.SENT_TO_CENTRAL_OPS.value: 3,
            FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value: 3,
            FLOW_STATUS.UPLOAD_KYC_DOCUMENT_VERIFIED_BY_CENTRAL_OPS.value: 4,
        }
        current_step = STATUS_TO_CURRENT_STEP.get(status, 0)
        
        if status == FLOW_STATUS.UPLOAD_KYC_DOCUMENT_VERIFIED_BY_CENTRAL_OPS.value:
            return 4
        else:
            return min(current_step + 1, total_steps)
    
    # Lead Generation
    elif flow_desc == "Lead Generation":
        STATUS_TO_CURRENT_STEP = {
            FLOW_STATUS.LEAD_GENERATION_STARTED.value: 0,
            FLOW_STATUS.ADD_LEAD_DETAILS.value: 1,  # Step 1 done
            FLOW_STATUS.LEAD_OTP_VERIFIED.value: 2,  # Step 2 done
            FLOW_STATUS.LEAD_GENERATION_COMPLETED.value: 3,  # Complete
        }
        current_step = STATUS_TO_CURRENT_STEP.get(status, 0)
        
        if status == FLOW_STATUS.LEAD_GENERATION_COMPLETED.value:
            return 3  # Stay at step 3
        else:
            return min(current_step + 1, total_steps)

    elif flow_desc == "Lead Closure":
        STATUS_TO_CURRENT_STEP = {
            FLOW_STATUS.LEAD_CLOSURE_STARTED.value: 0,
            FLOW_STATUS.LEAD_CLOSURE_DETAILS_ADDED.value: 1,
            FLOW_STATUS.LEAD_CLOSURE_COMPLETED.value: 2,
        }
        current_step = STATUS_TO_CURRENT_STEP.get(status, 0)

        if status == FLOW_STATUS.LEAD_CLOSURE_COMPLETED.value:
            return 2
        else:
            return min(current_step + 1, total_steps)
    
    # Default fallback
    return 1
def _is_last_flow(tracker):
    task = tracker.subtask.task
    last_order = TaskFlow.objects.filter(task=task).aggregate(Max("order")).get("order__max")
    if last_order is None:
        return False
    order = TaskFlow.objects.filter(task=task, flow=tracker.flow).values_list("order", flat=True).first()
    if order is None:
        return False
    return order == last_order
def _update_task_aggregate(task, user=None):
    total = task.subtasks.count()
    if total <= 0:
        return
    completed_count = task.subtasks.filter(status=SUBTASK_STATUS.COMPLETED.value).count()
    in_progress_exists = task.subtasks.filter(status=SUBTASK_STATUS.IN_PROGRESS.value).exists()
    if completed_count == total:
        task.status = TASK_STATUS.COMPLETED.value
        task.progress = 100
        task.completed = True
    else:
        task.status = TASK_STATUS.IN_PROGRESS.value if (in_progress_exists or completed_count > 0) else TASK_STATUS.YET_TO_START.value
        task.progress = (completed_count * 100) // total
        task.completed = False
    if user:
        task.modified_by = user
    task.save(update_fields=["status", "progress", "completed", "modified_by"])
def _is_flow_completed(tracker):
    status = tracker.flow_status
    return status in {
        FLOW_STATUS.LOCATION_VERIFICATION_VERIFIED_BY_CENTRAL_OPS.value,
        FLOW_STATUS.LOCATION_RE_VERIFICATION_VERIFIED_BY_CENTRAL_OPS.value,
        FLOW_STATUS.UPLOAD_KYC_DOCUMENT_VERIFIED_BY_CENTRAL_OPS.value,
        FLOW_STATUS.LEAD_GENERATION_COMPLETED.value,
        FLOW_STATUS.LEAD_CLOSURE_COMPLETED.value,
        FLOW_STATUS.VERIFIED_BY_CENTRAL_OPS.value,
    }
def _initialize_approval_flow(tracker):
    """
    Initialize approval records for field agent steps only.
    Excludes the final "ops approval/verification" step.
    """
    # Check if already initialized
    if tracker.step_approvals.exists():
        print(f"Approval flow already initialized for tracker {tracker.id}")
        return False
    
    # Get all flow steps
    all_steps = tracker.flow.flow_steps.all().order_by('step_order')
    
    if not all_steps.exists():
        print(f"No flow steps found for tracker {tracker.id}")
        return False
    
    # Identify ops approval steps (exclude them)
    ops_keywords = [
        'verify', 'verification', 'approval', 'opp team', 
        'central ops', 'automatically marked', 'marked as completed',
        'mark complete'
    ]
    
    field_agent_steps = []
    for step in all_steps:
        desc_lower = step.step_description.lower()
        is_ops_step = any(keyword in desc_lower for keyword in ops_keywords)
        if not is_ops_step:
            field_agent_steps.append(step)
        else:
            print(f"Excluding ops step: {step.step_description}")
    
    if not field_agent_steps:
        print(f"No field agent steps found for tracker {tracker.id}")
        return False
    
    # Create approval records
    approval_records = [
        SubTaskApproval(
            subtask_tracker=tracker,
            flow_step=step,
            step_order=step.step_order,
            approval_status=SubTaskApproval.ApprovalStatus.SUBMITTED
        )
        for step in field_agent_steps
    ]
    
    SubTaskApproval.objects.bulk_create(approval_records)
    print(f"Created {len(approval_records)} approval records for tracker {tracker.id}")
    
    # Set current_review_step and save immediately
    tracker.current_review_step = 1
    tracker.save(update_fields=['current_review_step'])
    print(f"Set current_review_step to 1 for tracker {tracker.id}")
    
    return True
        # Don't set progress to 100 yet - that happens after ops approves all steps
def _create_lead_from_tracker(tracker, user):
    payload = {
        "customer_name": tracker.full_name,
        "contact_number": tracker.phone_number,
        "product_category": tracker.product_category,
        "product_subcategory": tracker.product_sub_category,
        "amount": tracker.amount,
        "pincode": tracker.current_address_pincode,
        "source": tracker.lead_source,
        "lead_type": tracker.lead_type,
        "status": LeadStatus.UNVERIFIED.value,
    }
    print(f"Payload: {payload}")
    payloadUser = user or tracker.subtask.assign_to
    print(f"User: {payloadUser}")
    data = prepare_lead_create_data(payloadUser, payload)
    print(f"Lead create data: {data}")
    
    lead = create_lead(data)
    tracker.lead_id = lead.id
    tracker.save()
    print(f"Lead created: {lead}")
    return lead

class SubTaskTrackerView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            user = request.user
            params = request.query_params
            query = {}
            limit = request.GET.get("limit")
            page_limit = int(limit) if limit and limit.isdigit() else 10

            pg = request.GET.get("pg", "1")
            subtask_id = request.GET.get("subtask_id")
            flow_id = request.GET.get("flow_id")
            tracker_id = request.GET.get("id")
            search = request.GET.get("search")
            category_filter = request.GET.get("category")  # ✅ New category filter

            try:
                page_no = int(pg)
                offset = (page_no - 1) * page_limit
            except ValueError:
                return HttpResponse.BadRequest("Please send correct 'pg' param.")


            if tracker_id:
                query["id"] = tracker_id
            if subtask_id:
                query["subtask__id"] = subtask_id
            if flow_id:
                query["flow__id"] = flow_id

            queryset = (
                SubTaskTracker.objects
                .filter(**query)
                .select_related("subtask", "flow")
                .order_by("-id")
            )

            # DETAIL MODE: id provided → single tracker with approval meta
            if tracker_id:
                tracker = queryset.first()
                if not tracker:
                    return HttpResponse.BadRequest("SubTaskTracker not found")

                # Optional: prefetch approvals for performance
                tracker = (
                    SubTaskTracker.objects
                    .select_related("subtask", "flow")
                    .prefetch_related("step_approvals__corrections")
                    .get(id=tracker_id)
                )

                serializer = SubTaskTrackerGetSerializer(
                    tracker, context={"request": request}
                )
                return HttpResponse.Success({"subtask_tracker": serializer.data})
            if search:
                queryset = queryset.filter(
                    Q(subtask__task__task_id__icontains=search) | 
                    Q(central_ops_status__icontains=search)
                )

            # Serialize full queryset once so category counts are global (not per page)
            all_serialized = SubTaskTrackerGetSerializer(
                queryset, many=True, context={"request": request}
            )
            all_items = list(all_serialized.data)

            # Count categories from full queryset
            category_counts = {"approval": 0, "correction": 0, "rejected": 0, "completed": 0}
            for item in all_items:
                cat = item.get("category")
                if cat in category_counts:
                    category_counts[cat] += 1

            # Apply optional category filter before pagination
            if category_filter:
                valid_categories = {"approval", "correction", "rejected", "completed"}
                if category_filter not in valid_categories:
                    return HttpResponse.BadRequest(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
                filtered_items = [item for item in all_items if item.get("category") == category_filter]
            else:
                filtered_items = all_items

            # Paginate post-filtered items
            paginated_data = filtered_items[offset: offset + page_limit]

            return HttpResponse.Success({
                "subtask_trackers": paginated_data,
                "category_counts": category_counts,
                "total": len(filtered_items)
            })

        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    @transaction.atomic
    def post(self, request):
        try:
            data = request.data
            user = request.user

            print("data in subtask tracker post:", data)

            data["created_by"] = str(user.user_id)
            data["modified_by"] = str(user.user_id)
            data["step_number"] = 1
            flow_obj = Flow.objects.get(id=data.get("flow"))
            flow_desc = flow_obj.flow_description
            data["flow"] = flow_obj.id
            print("flow_desc:", flow_desc)

            if flow_desc == "Location Verification":
                data["flow_status"] = FLOW_STATUS.LOCATION_VERIFICATION_STARTED.value
            elif flow_desc == "Location Re-Verification":
                data["flow_status"] = FLOW_STATUS.LOCATION_RE_VERIFICATION_STARTED.value
            elif flow_desc == "Upload KYC Document":
                data["flow_status"] = FLOW_STATUS.UPLOAD_KYC_DOCUMENTS_STARTED.value
            elif flow_desc == "Lead Generation":
                data["flow_status"] = FLOW_STATUS.LEAD_GENERATION_STARTED.value
            elif flow_desc == "Lead Closure":
                data["flow_status"] = FLOW_STATUS.LEAD_CLOSURE_STARTED.value
            elif flow_desc == "Lead Closure (fulfilment)":
                data["flow_status"] = FLOW_STATUS.LEAD_CLOSURE_STARTED.value
            elif flow_desc == "Questionnaire":
                data["flow_status"] = FLOW_STATUS.QUESTIONNAIRE_STARTED.value
            else:
                data["flow_status"] = None

            serializer = SubTaskTrackerSerializer(data=data)
            if serializer.is_valid():
                subtask = SubTask.objects.get(id=data.get("subtask"))
                if subtask.status != SUBTASK_STATUS.IN_PROGRESS.value:
                    subtask.status = SUBTASK_STATUS.IN_PROGRESS.value
                    subtask.modified_by = user
                    subtask.save()
                _update_task_aggregate(subtask.task, user)
                tracker = serializer.save(created_by=user, modified_by=user)

                if not _initialize_approval_flow(tracker):
                    transaction.set_rollback(True)
                    return HttpResponse.BadRequest(
                        "This flow is not configured with reviewable steps. "
                        "Please add flow steps before creating a subtask tracker."
                    )

                response_serializer = SubTaskTrackerGetSerializer(
                    tracker, context={"request": request}
                )
                return HttpResponse.Success({"subtask_tracker": response_serializer.data})
            return HttpResponse.BadRequest(serializer.errors)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    @transaction.atomic
    def patch(self, request):
        try:
            data = request.data
            user = request.user
            tracker_id = request.GET.get("id")
            
            if not tracker_id:
                return HttpResponse.BadRequest("Missing tracker ID")
            
            app_name = request.GET.get("app_name")
            skip_phone_verification = app_name == "manipal"
            
            tracker = SubTaskTracker.objects.get(id=tracker_id)
            flow_desc = tracker.flow.flow_description
            
            # ========================================
            # LOCATION VERIFICATION FLOW
            # ========================================
            if flow_desc == "Location Verification":
                
                # Determine which steps need correction
                if tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value:
                    pending_corrections = list(tracker.step_approvals.filter(
                        approval_status=SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
                    ).values_list('step_order', flat=True))
                else:
                    pending_corrections = []
                
                # STEP 1
                if tracker.flow_status == FLOW_STATUS.LOCATION_VERIFICATION_STARTED.value:
                    tracker.flow_status = FLOW_STATUS.LOCATION_VERIFICATION_REACHED_ADDRESS.value
                    tracker.progress = 25
                    tracker.step_timestamps["LOCATION_VERIFICATION_REACHED_ADDRESS"] = get_ist_time_str()
                
                # STEP 1 CORRECTION
                elif tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value and 1 in pending_corrections:
                    tracker.flow_status = FLOW_STATUS.SENT_TO_CENTRAL_OPS.value
                
                # STEP 2
                elif tracker.flow_status in [FLOW_STATUS.LOCATION_VERIFICATION_REACHED_ADDRESS.value] or \
                    (tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value and 2 in pending_corrections):
                    
                    uploaded_file = request.FILES.get("location_photo")
                    if uploaded_file:
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.LOCATION_VERIFICATION.value,
                            document_type=FLOW_DOCUMENT_TYPE.LOCATION_PHOTO.value,
                            file=uploaded_file,
                            file_name=uploaded_file.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )
                    
                    if tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value:
                        tracker.flow_status = FLOW_STATUS.SENT_TO_CENTRAL_OPS.value
                    else:
                        tracker.flow_status = FLOW_STATUS.LOCATION_PHOTO_ADDED.value
                        tracker.progress = 50
                        tracker.step_timestamps["LOCATION_PHOTO_ADDED"] = get_ist_time_str()
                
                # STEP 3
                elif tracker.flow_status in [FLOW_STATUS.LOCATION_PHOTO_ADDED.value] or \
                    (tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value and 3 in pending_corrections):
                    
                    uploaded_file = request.FILES.get("selfie_photo")
                    if uploaded_file:
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.LOCATION_VERIFICATION.value,
                            document_type=FLOW_DOCUMENT_TYPE.SELFIE_PHOTO.value,
                            file=uploaded_file,
                            file_name=uploaded_file.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )
                    
                    if tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value:
                        tracker.flow_status = FLOW_STATUS.SENT_TO_CENTRAL_OPS.value
                    else:
                        tracker.flow_status = FLOW_STATUS.SELFIE_PHOTO_ADDED.value
                        tracker.progress = 75
                        tracker.step_timestamps["SELFIE_PHOTO_ADDED"] = get_ist_time_str()
                        _initialize_approval_flow(tracker)

            
            # ========================================
            # LOCATION RE-VERIFICATION FLOW
            # ========================================
            elif flow_desc == "Location Re-Verification":
                if tracker.flow_status == FLOW_STATUS.LOCATION_RE_VERIFICATION_STARTED.value:
                    # Step 1: Mark reached address
                    tracker.flow_status = FLOW_STATUS.LOCATION_RE_VERIFICATION_REACHED_ADDRESS.value
                    tracker.progress = 25
                    tracker.step_timestamps["REACHED_ADDRESS"] = get_ist_time_str()
                
                elif tracker.flow_status in [FLOW_STATUS.LOCATION_RE_VERIFICATION_REACHED_ADDRESS.value, FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value]:
                    # Step 2: Upload location photo
                    uploaded_file = request.FILES.get("location_photo")
                    if uploaded_file:
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.LOCATION_REVERIFICATION.value,
                            document_type=FLOW_DOCUMENT_TYPE.LOCATION_PHOTO.value,
                            file=uploaded_file,
                            file_name=uploaded_file.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )
                    
                    if tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value:
                        tracker.flow_status = FLOW_STATUS.SENT_TO_CENTRAL_OPS.value
                    else:
                        tracker.flow_status = FLOW_STATUS.LOCATION_PHOTO_ADDED.value
                        tracker.progress = 50
                        tracker.step_timestamps["LOCATION_PHOTO_ADDED"] = get_ist_time_str()
                
                elif tracker.flow_status in [FLOW_STATUS.LOCATION_PHOTO_ADDED.value, FLOW_STATUS.SENT_TO_CENTRAL_OPS.value]:
                    # Step 3: Upload selfie photo
                    uploaded_file = request.FILES.get("selfie_photo")
                    if uploaded_file:
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.LOCATION_REVERIFICATION.value,
                            document_type=FLOW_DOCUMENT_TYPE.SELFIE_PHOTO.value,
                            file=uploaded_file,
                            file_name=uploaded_file.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )
                    
                    if tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value:
                        tracker.flow_status = FLOW_STATUS.SENT_TO_CENTRAL_OPS.value
                    else:
                        tracker.flow_status = FLOW_STATUS.SELFIE_PHOTO_ADDED.value
                        tracker.progress = 75
                        tracker.step_timestamps["SELFIE_PHOTO_ADDED"] = get_ist_time_str()
                        # Initialize approval flow
                        _initialize_approval_flow(tracker)
            
            # ========================================
            # UPLOAD KYC DOCUMENT FLOW
            # ========================================
            elif flow_desc == "Upload KYC Document":
                
                # Determine which steps need correction (if any)
                if tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value:
                    pending_corrections = list(tracker.step_approvals.filter(
                        approval_status=SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
                    ).values_list('step_order', flat=True))
                else:
                    pending_corrections = []
                
                # ===== STEP 1: Visit merchant =====
                if tracker.flow_status == FLOW_STATUS.UPLOAD_KYC_DOCUMENTS_STARTED.value:
                    tracker.flow_status = FLOW_STATUS.KYC_REACHED_ADDRESS.value
                    tracker.progress = 25
                    tracker.step_timestamps["REACHED_ADDRESS"] = get_ist_time_str()
                
                # STEP 1 CORRECTION
                elif tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value and 1 in pending_corrections:
                    tracker.flow_status = FLOW_STATUS.SENT_TO_CENTRAL_OPS.value
                
                # ===== STEP 2: Upload ALL documents (PAN + Aadhaar + Other) - MERGED =====
                elif tracker.flow_status in [FLOW_STATUS.KYC_REACHED_ADDRESS.value] or \
                    (tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value and 2 in pending_corrections):
                    
                    print("="*50)
                    print("🔍 STEP 2: Document Upload Started")
                    print(f"Current flow_status: {tracker.flow_status}")
                    print(f"Pending corrections: {pending_corrections}")
                    print("="*50)
                    
                    # --- Handle PAN Card Upload ---
                    pan_card = request.FILES.get("pan_card")
                    if pan_card:
                        print(f"✅ PAN Card file received: {pan_card.name}")
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.KYC_DOCUMENT_UPLOAD.value,
                            document_type=FLOW_DOCUMENT_TYPE.PAN_CARD.value,
                            file=pan_card,
                            file_name=pan_card.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )
                    else:
                        print("⚠️ No PAN Card file in request")
                    
                    # Verify PAN
                    print(f"\n🔐 PAN Verification Check:")
                    print(f"  - tracker.is_pan_verify: {tracker.is_pan_verify} (type: {type(tracker.is_pan_verify)})")
                    print(f"  - data.get('is_zoop_pan_verify'): {data.get('is_zoop_pan_verify')} (type: {type(data.get('is_zoop_pan_verify'))})")
                    print(f"  - to_bool result: {to_bool(data.get('is_zoop_pan_verify'))}")
                    print(f"  - Combined condition: {tracker.is_pan_verify is True and to_bool(data.get('is_zoop_pan_verify'))}")
                    
                    if not (tracker.is_pan_verify is True and to_bool(data.get("is_zoop_pan_verify"))):
                        print("❌ PAN Verification FAILED - returning error")
                        return HttpResponse.BadRequest("PAN Verification pending")
                    
                    # Save PAN details
                    tracker.pan_number = data.get("pan_number")
                    tracker.is_zoop_pan_verify = True
                    tracker.step_timestamps["PAN_CARD_VERIFIED"] = get_ist_time_str()
                    print(f"✅ PAN Verified - Number: {tracker.pan_number}")
                    
                    # --- Handle Aadhaar Card Upload ---
                    print("\n" + "="*50)
                    print("📄 AADHAAR PROCESSING STARTED")
                    print("="*50)
                    
                    front_aadhar = request.FILES.get("front_aadhar_card")
                    back_aadhar = request.FILES.get("back_aadhar_card")
                    
                    print(f"Front Aadhaar file present: {front_aadhar is not None}")
                    print(f"Back Aadhaar file present: {back_aadhar is not None}")
                    
                    if front_aadhar:
                        print(f"✅ Front Aadhaar file: {front_aadhar.name}")
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.KYC_DOCUMENT_UPLOAD.value,
                            document_type=FLOW_DOCUMENT_TYPE.FRONT_AADHAR_CARD.value,
                            file=front_aadhar,
                            file_name=front_aadhar.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )
                    else:
                        print("⚠️ No Front Aadhaar file in request")
                    
                    if back_aadhar:
                        print(f"✅ Back Aadhaar file: {back_aadhar.name}")
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.KYC_DOCUMENT_UPLOAD.value,
                            document_type=FLOW_DOCUMENT_TYPE.BACK_AADHAR_CARD.value,
                            file=back_aadhar,
                            file_name=back_aadhar.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )
                    else:
                        print("⚠️ No Back Aadhaar file in request")
                    
                    # ⚠️ CRITICAL DEBUG SECTION - Verify Aadhaar
                    print("\n" + "🔍 AADHAAR VERIFICATION DEBUG:")
                    print("-" * 50)
                    
                    aadhar_from_request = data.get("aadhar_number", "")
                    zoop_aadhar_from_request = data.get("zoop_aadhar", "")
                    
                    print(f"📥 Raw data from request:")
                    print(f"  - data.get('aadhar_number'): '{aadhar_from_request}' (type: {type(aadhar_from_request)})")
                    print(f"  - data.get('zoop_aadhar'): '{zoop_aadhar_from_request}' (type: {type(zoop_aadhar_from_request)})")
                    
                    aadhar_digits = re.sub(r"\D", "", str(aadhar_from_request))
                    zoop_aadhar_digits = re.sub(r"\D", "", str(zoop_aadhar_from_request))
                    aadhar_last_4 = aadhar_digits[-4:] if aadhar_digits else ""
                    aadhar_first2_last2 = (aadhar_digits[:2] + aadhar_digits[-2:]) if len(aadhar_digits) >= 4 else ""
                    zoop_last_4 = zoop_aadhar_digits[-4:] if zoop_aadhar_digits else ""
                    
                    print(f"\n🔢 Processed values:")
                    print(f"  - str(aadhar_number): '{str(aadhar_from_request)}' -> digits: '{aadhar_digits}'")
                    print(f"  - aadhar last4: '{aadhar_last_4}'")
                    print(f"  - aadhar first2+last2: '{aadhar_first2_last2}'")
                    print(f"  - str(zoop_aadhar): '{str(zoop_aadhar_from_request)}' -> digits: '{zoop_aadhar_digits}'")
                    print(f"  - zoop extracted 4 digits: '{zoop_last_4}'")
                    
                    print(f"\n⚖️ Comparison:")
                    print(f"  - match last4? {aadhar_last_4 == zoop_last_4}")
                    print(f"  - match first2+last2? {aadhar_first2_last2 == zoop_last_4}")
                    
                    print(f"\n🗄️ Current tracker values BEFORE validation:")
                    print(f"  - tracker.aadhar_number: {tracker.aadhar_number}")
                    print(f"  - tracker.is_aadhar_verify: {tracker.is_aadhar_verify}")
                    
                    print("-" * 50)
                    
                    # Accept either: exact last 4 match OR first2+last2 match (per current Govt response)
                    valid_last4 = (len(aadhar_last_4) == 4 and len(zoop_last_4) == 4 and aadhar_last_4 == zoop_last_4)
                    valid_first2_last2 = (len(aadhar_first2_last2) == 4 and len(zoop_last_4) == 4 and aadhar_first2_last2 == zoop_last_4)
                    if not (valid_last4 or valid_first2_last2):
                        print("❌❌❌ AADHAAR VERIFICATION FAILED ❌❌❌")
                        print(f"aadhar last4: '{aadhar_last_4}', aadhar first2+last2: '{aadhar_first2_last2}', zoop: '{zoop_last_4}'")
                        return HttpResponse.BadRequest("Aadhar Verification pending")
                    
                    print("✅✅✅ AADHAAR VERIFICATION PASSED ✅✅✅")
                    
                    # Save Aadhaar details
                    tracker.is_aadhar_verify = True
                    tracker.aadhar_number = data.get("aadhar_number")
                    tracker.step_timestamps["AADHAR_CARD_VERIFIED"] = get_ist_time_str()
                    
                    print(f"\n💾 Aadhaar details saved to tracker:")
                    print(f"  - tracker.aadhar_number: {tracker.aadhar_number}")
                    print(f"  - tracker.is_aadhar_verify: {tracker.is_aadhar_verify}")
                    print(f"  - Timestamp: {tracker.step_timestamps.get('AADHAR_CARD_VERIFIED')}")
                    
                    # --- Handle Other Documents (Optional) ---
                    print("\n" + "="*50)
                    print("📋 OTHER DOCUMENTS PROCESSING")
                    print("="*50)
                    
                    front_other = request.FILES.get("front_other_document")
                    back_other = request.FILES.get("back_other_document")
                    other_doc_type = data.get("other_document_type")
                    
                    print(f"Other document type: {other_doc_type}")
                    print(f"Front other document present: {front_other is not None}")
                    print(f"Back other document present: {back_other is not None}")
                    
                    # Determine document types
                    front_document_type = None
                    back_document_type = None
                    
                    if other_doc_type == OTHER_DOCUMENTS.DRIVING_LICENSE.value:
                        front_document_type = FLOW_DOCUMENT_TYPE.FRONT_DRIVING_LICENSE.value
                        back_document_type = FLOW_DOCUMENT_TYPE.BACK_DRIVING_LICENSE.value
                        print(f"✅ Document type: DRIVING LICENSE")
                    elif other_doc_type == OTHER_DOCUMENTS.PASSPORT.value:
                        front_document_type = FLOW_DOCUMENT_TYPE.FRONT_PASSPORT.value
                        back_document_type = FLOW_DOCUMENT_TYPE.BACK_PASSPORT.value
                        print(f"✅ Document type: PASSPORT")
                    elif other_doc_type == OTHER_DOCUMENTS.VOTER_ID.value:
                        front_document_type = FLOW_DOCUMENT_TYPE.FRONT_VOTER_ID.value
                        back_document_type = FLOW_DOCUMENT_TYPE.BACK_VOTER_ID.value
                        print(f"✅ Document type: VOTER ID")
                    else:
                        print(f"⚠️ No valid other document type specified")
                    
                    # Upload other documents if provided
                    if front_other and front_document_type:
                        print(f"✅ Uploading front other document: {front_other.name}")
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.KYC_DOCUMENT_UPLOAD.value,
                            document_type=front_document_type,
                            file=front_other,
                            file_name=front_other.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )
                    
                    if back_other and back_document_type:
                        print(f"✅ Uploading back other document: {back_other.name}")
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.KYC_DOCUMENT_UPLOAD.value,
                            document_type=back_document_type,
                            file=back_other,
                            file_name=back_other.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )
                    
                    # Mark other documents as verified if provided
                    print(f"\n🔐 Other document verification:")
                    print(f"  - other_document_type: {other_doc_type}")
                    print(f"  - data.get('other_document_verified'): {data.get('other_document_verified')}")
                    print(f"  - to_bool result: {to_bool(data.get('other_document_verified'))}")
                    
                    if other_doc_type and to_bool(data.get("other_document_verified")):
                        tracker.other_document = other_doc_type
                        tracker.other_document_verified = True
                        tracker.step_timestamps["OTHER_DOCUMENTS_VERIFIED"] = get_ist_time_str()
                        print(f"✅ Other documents marked as verified")
                    else:
                        print(f"⚠️ Other documents not verified or not provided")
                    
                    # ✅ Update final status for Step 2
                    print("\n" + "="*50)
                    print("🎯 FINALIZING STEP 2 STATUS")
                    print(f"Current flow_status before update: {tracker.flow_status}")
                    
                    if tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value:
                        tracker.flow_status = FLOW_STATUS.SENT_TO_CENTRAL_OPS.value
                        print(f"✅ Status updated to: SENT_TO_CENTRAL_OPS (correction flow)")
                    else:
                        # ✅ Final status: DOCUMENTS_VERIFIED (not OTHER_DOCUMENTS_VERIFIED)
                        tracker.flow_status = FLOW_STATUS.DOCUMENTS_VERIFIED.value
                        tracker.progress = 50
                        print(f"✅ Status updated to: DOCUMENTS_VERIFIED")
                        print(f"✅ Progress updated to: 50%")
                    
                    print("="*50 + "\n")

                
                # ===== STEP 3: Capture ALL customer details + address (MERGED) =====

                elif tracker.flow_status in [FLOW_STATUS.DOCUMENTS_VERIFIED.value] or \
                    (tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value and 3 in pending_corrections):
                    
                    print("="*50)
                    print("🔍 STEP 3: Customer Details Capture Started")
                    print("="*50)
                    
                    # Capture customer details
                    tracker.full_name = data.get("full_name", tracker.full_name)
                    
                    # Handle date_of_birth conversion from DD-MM-YYYY to YYYY-MM-DD
                    dob_input = data.get("date_of_birth")
                    if dob_input:
                        try:
                            print(f"📅 Date of Birth conversion:")
                            print(f"  - Input (DD-MM-YYYY): {dob_input}")
                            
                            # Parse DD-MM-YYYY format
                            dob_parsed = datetime.strptime(str(dob_input), "%d-%m-%Y")
                            # Convert to YYYY-MM-DD format
                            tracker.date_of_birth = dob_parsed.strftime("%Y-%m-%d")
                            
                            print(f"  - Converted (YYYY-MM-DD): {tracker.date_of_birth}")
                            print(f"  ✅ Date conversion successful")
                        except ValueError as e:
                            print(f"  ❌ Date conversion failed: {e}")
                            print(f"  - Attempting alternate format (YYYY-MM-DD)")
                            try:
                                # Check if it's already in YYYY-MM-DD format
                                dob_parsed = datetime.strptime(str(dob_input), "%Y-%m-%d")
                                tracker.date_of_birth = dob_input
                                print(f"  ✅ Date already in correct format")
                            except ValueError:
                                print(f"  ❌ Invalid date format. Expected DD-MM-YYYY or YYYY-MM-DD")
                                return HttpResponse.BadRequest("Invalid date_of_birth format. Expected DD-MM-YYYY")
                    else:
                        print(f"📅 No new date_of_birth provided, keeping existing: {tracker.date_of_birth}")
                    
                    tracker.gender = data.get("gender", tracker.gender)
                    tracker.father_name = data.get("father_name", tracker.father_name)
                    tracker.email = data.get("email", tracker.email)
                    tracker.phone_number = data.get("phone_number", tracker.phone_number)
                    tracker.whatsapp_number = data.get("whatsapp_number", tracker.whatsapp_number)
                    tracker.profession = data.get("profession", tracker.profession)
                    
                    print(f"\n👤 Customer Details:")
                    print(f"  - Full Name: {tracker.full_name}")
                    print(f"  - Date of Birth: {tracker.date_of_birth}")
                    print(f"  - Gender: {tracker.gender}")
                    print(f"  - Father Name: {tracker.father_name}")
                    print(f"  - Email: {tracker.email}")
                    print(f"  - Phone: {tracker.phone_number}")
                    print(f"  - WhatsApp: {tracker.whatsapp_number}")
                    print(f"  - Profession: {tracker.profession}")
                    
                    # Capture address details
                    tracker.permanent_address = data.get("permanent_address", tracker.permanent_address)
                    tracker.permanent_address_pincode = data.get("permanent_address_pincode", tracker.permanent_address_pincode)
                    tracker.permanent_address_state = data.get("permanent_address_state", tracker.permanent_address_state)
                    tracker.permanent_address_city = data.get("permanent_address_city", tracker.permanent_address_city)
                    tracker.permanent_address_district = data.get("permanent_address_district", tracker.permanent_address_district)
                    tracker.current_address_state = data.get("current_address_state", tracker.current_address_state)
                    tracker.current_address_district = data.get("current_address_district", tracker.current_address_district)
                    tracker.current_address_city = data.get("current_address_city", tracker.current_address_city)
                    tracker.current_address_pincode = data.get("current_address_pincode", tracker.current_address_pincode)
                    tracker.current_address = data.get("current_address", tracker.current_address)
                    
                    print(f"\n🏠 Address Details:")
                    print(f"  - Permanent: {tracker.permanent_address}, {tracker.permanent_address_city}")
                    print(f"  - Current: {tracker.current_address}, {tracker.current_address_city}")
                    
                    # Upload profile pic
                    profile_pic = request.FILES.get("profile_pic")
                    if profile_pic:
                        print(f"\n📸 Profile Picture:")
                        print(f"  - File: {profile_pic.name}")
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.KYC_DOCUMENT_UPLOAD.value,
                            document_type=FLOW_DOCUMENT_TYPE.PROFILE_PIC.value,
                            file=profile_pic,
                            file_name=profile_pic.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )
                        print(f"  ✅ Profile picture uploaded")
                    else:
                        print(f"\n📸 No profile picture in request")

                    
                    # Validate phone verification
                    if not (skip_phone_verification or to_bool(tracker.is_phone_verified)):
                        # return HttpResponse.BadRequest("Phone verification pending")
                        pass # TODO: change after demo
                    
                    # Validate all required fields
                    required_fields = [
                        tracker.permanent_address,
                        tracker.permanent_address_pincode,
                        tracker.permanent_address_state,
                        tracker.permanent_address_city,
                        tracker.permanent_address_district,
                        tracker.current_address_state,
                        tracker.current_address_district,
                        tracker.current_address_city,
                        tracker.current_address_pincode,
                        tracker.current_address,
                    ]
                    
                    if not all(required_fields):
                        return HttpResponse.BadRequest("Please complete all address details.")
                    
                    # ✅ All validations passed
                    if tracker.flow_status == FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value:
                        tracker.flow_status = FLOW_STATUS.SENT_TO_CENTRAL_OPS.value
                    else:
                        tracker.flow_status = FLOW_STATUS.CUSTOMER_DETAILS_ADDED.value
                        tracker.progress = 75
                        tracker.step_timestamps["CUSTOMER_DETAILS_ADDED"] = get_ist_time_str()
                        # Initialize approval flow
                        _initialize_approval_flow(tracker)


            
            # ========================================
            # LEAD GENERATION FLOW
            # ========================================
            elif flow_desc == "Lead Generation":
                if tracker.flow_status == FLOW_STATUS.LEAD_GENERATION_STARTED.value:
                    # Step 1: Add lead details
                    tracker.full_name = data.get("full_name", tracker.full_name)
                    tracker.phone_number = data.get("phone_number", tracker.phone_number)
                    tracker.current_address_pincode = data.get("current_address_pincode", tracker.current_address_pincode)
                    tracker.current_address_state = data.get("current_address_state", tracker.current_address_state)
                    tracker.current_address_district = data.get("current_address_district", tracker.current_address_district)
                    tracker.product_category = data.get("product_category", tracker.product_category)
                    tracker.product_sub_category = data.get("product_sub_category", tracker.product_sub_category)
                    tracker.amount = data.get("amount", tracker.amount)
                    tracker.lead_source = data.get("lead_source", tracker.lead_source)
                    tracker.lead_type = data.get("lead_type", tracker.lead_type)

                    
                    if (
                        tracker.full_name and
                        tracker.phone_number and
                        tracker.current_address_pincode and
                        tracker.current_address_state and
                        tracker.current_address_district and
                        tracker.product_category and
                        tracker.product_sub_category and
                        tracker.amount and
                        tracker.lead_source and
                        tracker.lead_type
                    ):
                        try:
                            # Create lead BEFORE updating status - if it fails, tracker remains in STARTED status
                            _create_lead_from_tracker(tracker, tracker.subtask.assign_to or user)
                            
                            tracker.flow_status = FLOW_STATUS.ADD_LEAD_DETAILS.value
                            tracker.progress = 50
                            tracker.step_timestamps["ADD_LEAD_DETAILS"] = get_ist_time_str()
                            print(f"  ✅ Lead details added")
                        except ValueError as ve:
                            # Handle validation errors from create_lead (LeadCreateSerializer)
                            # Extract the first error message from the serializer errors dictionary
                            errors = ve.args[0]
                            if isinstance(errors, dict):
                                for field in errors:
                                    if isinstance(errors[field], list) and errors[field]:
                                        return HttpResponse.BadRequest(errors[field][0])
                                    elif isinstance(errors[field], str):
                                        return HttpResponse.BadRequest(errors[field])
                            return HttpResponse.BadRequest(str(errors))
                        except Exception as e:
                            # Catch-all for other lead creation failures
                            traceback.print_exc()
                            return HttpResponse.BadRequest(f"Lead creation failed: {str(e)}")
                    else:
                        return HttpResponse.BadRequest("Please complete all lead details.")
                
                elif tracker.flow_status == FLOW_STATUS.ADD_LEAD_DETAILS.value:
                    # Step 2: OTP verification - auto-completes flow
                    if skip_phone_verification or to_bool(data.get("is_phone_verified")):
                        tracker.flow_status = FLOW_STATUS.LEAD_OTP_VERIFIED.value
                        tracker.progress = 100
                        tracker.is_phone_verified = True
                        tracker.step_timestamps["LEAD_OTP_VERIFIED"] = get_ist_time_str()
                        
                        # Award rewards for lead generation
                        if tracker.reward > 0 and tracker.subtask.assign_to:
                            from users.models import UserReward
                            
                            description = f"Reward for completing {tracker.flow.flow_description}"
                            today = timezone.now().date()
                            
                            existing = UserReward.objects.filter(
                                user=tracker.subtask.assign_to,
                                description=description,
                                amount=tracker.reward,
                                created_at__date=today
                            ).exists()
                            
                            if not existing:
                                UserReward.objects.create(
                                    user=tracker.subtask.assign_to,
                                    amount=tracker.reward,
                                    description=description
                                )
                    else:
                        return HttpResponse.BadRequest("OTP verification pending")
                
                elif tracker.flow_status == FLOW_STATUS.LEAD_OTP_VERIFIED.value:
                    tracker.flow_status = FLOW_STATUS.LEAD_GENERATION_COMPLETED.value
                    tracker.step_timestamps["TASK_COMPLETED"] = get_ist_time_str()
                    
                    # Verify the lead after mark as done
                    if tracker.lead_id:
                        try:
                            lead = LeadV2.objects.get(id=tracker.lead_id)
                            if lead.status == LeadStatus.UNVERIFIED:
                                lead.status = LeadStatus.ACTIVE
                                lead.save()
                                print(f"  ✅ Lead {lead.id} verified (status set to ACTIVE)")
                        except LeadV2.DoesNotExist:
                            print(f"  ⚠️ Lead {tracker.lead_id} not found for verification")

            elif flow_desc == "Lead Closure":
                if tracker.flow_status == FLOW_STATUS.LEAD_CLOSURE_STARTED.value:
                    tracker.customer_id = data.get("customer_id", tracker.customer_id)
                    tracker.full_name = data.get("full_name", tracker.full_name)
                    tracker.amount = data.get("amount", tracker.amount)
                    tracker.loan_account_number = data.get("loan_account_number", tracker.loan_account_number)
                    tracker.product_category = data.get("product_category", tracker.product_category)
                    tracker.product_sub_category = data.get("product_sub_category", tracker.product_sub_category)
                    tracker.bank_name = data.get("bank_name", tracker.bank_name)
                    tracker.lead_type = data.get("lead_type", tracker.lead_type)

                    loan_date_input = data.get("loan_date")
                    if loan_date_input:
                        try:
                            tracker.loan_date = datetime.strptime(str(loan_date_input), "%d-%m-%Y").date()
                        except ValueError:
                            try:
                                tracker.loan_date = datetime.strptime(str(loan_date_input), "%Y-%m-%d").date()
                            except ValueError:
                                return HttpResponse.BadRequest("Invalid loan_date format")

                    pledge_card = request.FILES.get("pledge_card_kfs")
                    if pledge_card:
                        SubTaskDocument.objects.create(
                            document_flow=DOCUMENT_FLOW.LEAD_CLOSURE.value,
                            document_type=FLOW_DOCUMENT_TYPE.PLEDGE_CARD_KFS.value,
                            file=pledge_card,
                            file_name=pledge_card.name,
                            subtask=tracker.subtask,
                            uploaded_by=user,
                        )

                    required_fields = [
                        tracker.customer_id,
                        tracker.full_name,
                        tracker.amount,
                        tracker.loan_date,
                        tracker.loan_account_number,
                        tracker.product_category,
                        tracker.product_sub_category,
                        tracker.bank_name,
                        tracker.lead_type,
                    ]

                    if not all(required_fields):
                        return HttpResponse.BadRequest("Please complete all servicing details.")

                    tracker.flow_status = FLOW_STATUS.LEAD_CLOSURE_DETAILS_ADDED.value
                    tracker.progress = 50
                    tracker.step_timestamps["LEAD_CLOSURE_DETAILS_ADDED"] = get_ist_time_str()

                elif tracker.flow_status == FLOW_STATUS.LEAD_CLOSURE_DETAILS_ADDED.value:
                    tracker.flow_status = FLOW_STATUS.LEAD_CLOSURE_COMPLETED.value
                    tracker.progress = 100
                    tracker.step_timestamps["LEAD_CLOSURE_COMPLETED"] = get_ist_time_str()
            
            # ========================================
            # COMMON LOGIC FOR ALL FLOWS - ONLY AFTER SUCCESS
            # ========================================
            
            # Update step number based on completed timestamps
            tracker.step_number = _get_step_number_from_status(tracker)
            tracker.modified_by = user
            tracker.save()
            
            if (to_bool(tracker.is_last) or _is_last_flow(tracker)) and _is_flow_completed(tracker):
                subtask = SubTask.objects.get(id=tracker.subtask.id)
                if subtask.status != SUBTASK_STATUS.COMPLETED.value:
                    subtask.status = SUBTASK_STATUS.COMPLETED.value
                    subtask.modified_by = user
                    subtask.save()
                if "TASK_COMPLETED" not in tracker.step_timestamps:
                    tracker.step_timestamps["TASK_COMPLETED"] = get_ist_time_str()
                    tracker.save(update_fields=["step_timestamps"])
                _update_task_aggregate(subtask.task, user)
            else:
                _update_task_aggregate(tracker.subtask.task, user)
            
            # Return success response
            serializer = SubTaskTrackerDetailSerializer(tracker)
            return HttpResponse.Success({"subtask_tracker": serializer.data})
        
        except SubTaskTracker.DoesNotExist:
            return HttpResponse.NotFound("SubTaskTracker not found")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

class PanOtpSendView(APIView):
    def post(self, request):
        data = request.data
        try:
            tracker_id = request.GET.get("tracker_id")
            user_id = request.GET.get("user_id")
            phone_number = data.get("phone_number")

            # CASE 1 ► tracker_id provided → send OTP via tracker flow
            if tracker_id:
                tracker = SubTaskTracker.objects.get(id=tracker_id)
                phone_number = phone_number or tracker.subtask.contact_person_number

                if not phone_number:
                    return HttpResponse.BadRequest("No phone number found.")

                otp = generate_otp()
                tracker.pan_otp = otp
                tracker.pan_otp_created_at = timezone.now()
                tracker.save()

                print(f"PAN OTP for tracker → {phone_number}: {otp}")
                try:
                    if tracker.flow.flow_description == "Lead Generation":
                        SMSService().sendLeadGenerationOtp(mobile=phone_number, otp=otp)
                    else:
                        SMSService().sendPanVerificationOtp(
                            mobile=phone_number,
                            otp=otp,
                            lead_type=tracker.lead_type,
                        )
                except Exception as e:
                    print(f"Failed to send PAN OTP SMS to {phone_number}: {e}")
                resp = {"message": f"OTP sent to {phone_number},", "otp": otp}
                try:
                    if ((getattr(environment, "APP_ENV", "") or "").upper() != "PROD") and getattr(environment, "MASTER_OTP", None):
                        resp["master_otp"] = environment.MASTER_OTP
                except Exception:
                    pass
                return HttpResponse.Success(resp)

            # CASE 2 ► user_id provided → send OTP to User
            if user_id:
                user = User.objects.get(user_id=user_id)
                phone_number = phone_number

                if not phone_number:
                    return HttpResponse.BadRequest("User has no phone number.")

                otp = generate_otp()
                user.phone_otp = otp
                user.phone_otp_created_at = timezone.now()
                user.save()

                print(f"Phone OTP for user → {phone_number}: {otp}")
                try:
                    SMSService().sendPanVerificationOtp(mobile=phone_number, otp=otp)
                except Exception as e:
                    print(f"Failed to send phone OTP SMS to {phone_number}: {e}")
                resp = {"message": f"OTP sent to {phone_number}"}
                # try:
                #     if ((getattr(environment, "APP_ENV", "") or "").upper() != "PROD") and getattr(environment, "MASTER_OTP", None):
                #         resp["master_otp"] = environment.MASTER_OTP
                # except Exception:
                #     pass
                return HttpResponse.Success(resp)

            return HttpResponse.BadRequest("Provide tracker_id, user_id, or phone_number.")

        except SubTaskTracker.DoesNotExist:
            return HttpResponse.NotFound("Tracker not found.")
        except User.DoesNotExist:
            return HttpResponse.NotFound("User not found.")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class PanOtpVerifyView(APIView):
    def post(self, request):
        try:
            tracker_id = request.GET.get("tracker_id")
            user_id = request.GET.get("user_id")
            phone_number = request.data.get("phone_number")
            otp = request.data.get("otp")

            if not otp:
                return HttpResponse.BadRequest("OTP is required.")

            # CASE 1 ► Verify using tracker
            if tracker_id:
                tracker = SubTaskTracker.objects.get(id=tracker_id)

                if is_otp_valid(tracker, otp):
                    if to_bool(tracker.is_pan_verify):
                        tracker.is_phone_verified = True
                    else:
                        tracker.is_pan_verify = True

                    tracker.pan_otp = None
                    tracker.pan_otp_created_at = None
                    
                    tracker.save()
                    return HttpResponse.Success({"message": "Tracker OTP verified successfully."})
                
                return HttpResponse.BadRequest("Invalid or expired OTP.")

            # CASE 2 ► Verify using user_id
            if user_id:
                user = User.objects.get(user_id=user_id)

                if is_otp_valid(user, otp):
                    user.is_phone_verified = True
                    user.phone_otp = None
                    user.phone_otp_created_at = None
                    user.save()

                    return HttpResponse.Success({"message": "User OTP verified successfully."})
                
                return HttpResponse.BadRequest("Invalid or expired OTP.")

            return HttpResponse.BadRequest("Provide tracker_id, user_id, or phone_number.")

        except SubTaskTracker.DoesNotExist:
            return HttpResponse.NotFound("Tracker not found.")
        except User.DoesNotExist:
            return HttpResponse.NotFound("User not found.")
        except Exception as e:
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))
