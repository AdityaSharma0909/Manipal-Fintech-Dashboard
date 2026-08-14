# task/views_approval.py - NEW FILE

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404

from tasks.models import SubTaskTracker, SubTaskApproval, StepCorrection
from tasks.serializers import (
    SubTaskTrackerApprovalDetailSerializer,
    CentralOpsReviewSerializer,FinalApprovalSerializer
)
from flows.models import Flow, FlowStep
from utils.constants import CORRECTION_REASONS, FLOW_STATUS
from utils.responseHandler import HttpResponse

class CentralOpsReviewView(APIView):
    """
    Central Ops endpoint to REVIEW or SEND BACK a specific flow step.
    - Central Ops can ONLY mark steps as REVIEWED
    - Final approval & rewards happen ONLY in FinalTrackerApprovalView
    """
    permission_classes = []

    @transaction.atomic
    def post(self, request):
        try:
            serializer = CentralOpsReviewSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)

            data = serializer.validated_data
            tracker = get_object_or_404(SubTaskTracker, id=data['tracker_id'])

            step_approval = get_object_or_404(
                SubTaskApproval,
                subtask_tracker=tracker,
                step_order=data['step_order']
            )

            # Step must be in reviewable state
            if step_approval.approval_status not in [
                SubTaskApproval.ApprovalStatus.SUBMITTED,
                SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
            ]:
                return HttpResponse.BadRequest(
                    f"Step {data['step_order']} is not ready for review. "
                    f"Current status: {step_approval.approval_status}"
                )

            if data['action'] == 'REVIEW':
                self._review_step(step_approval, tracker, request.user)
                message = f"Step {data['step_order']} reviewed successfully"

            elif data['action'] == 'SEND_BACK':
                self._send_back_step(
                    step_approval,
                    tracker,
                    data['correction_reason'],
                    data.get('correction_comment', ''),
                    request.user
                )
                message = f"Step {data['step_order']} sent back for correction"

            else:
                return HttpResponse.BadRequest("Invalid action")

            serializer = SubTaskTrackerApprovalDetailSerializer(tracker)
            return HttpResponse.Success({
                'message': message,
                'tracker': serializer.data
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def _review_step(self, step_approval, tracker, user):
        """
        Mark a step as REVIEWED and move to the next pending step.
        """
        step_approval.approval_status = SubTaskApproval.ApprovalStatus.REVIEWED
        step_approval.approved_by = user
        step_approval.approved_at = timezone.now()
        step_approval.save()

        # Resolve resubmitted corrections
        step_approval.corrections.filter(
            status=StepCorrection.CorrectionStatus.RESUBMITTED
        ).update(
            status=StepCorrection.CorrectionStatus.RESOLVED,
            resolved_at=timezone.now()
        )

        self._recalculate_current_review_step(tracker)
        tracker.save()

    def _send_back_step(self, step_approval, tracker, reason, comment, user):
        """
        Send a step back for correction.
        """
        step_approval.approval_status = SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
        step_approval.save()

        StepCorrection.objects.create(
            flow_step_approval=step_approval,
            reason=reason,
            comment=comment,
            corrected_by=user,
            status=StepCorrection.CorrectionStatus.PENDING_CORRECTION
        )

        tracker.flow_status = FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value
        tracker.central_ops_user = user

        self._recalculate_current_review_step(tracker)
        tracker.save()

    def _recalculate_current_review_step(self, tracker):
        """
        Set current_review_step to the lowest pending step order.
        """
        pending = tracker.step_approvals.filter(
            approval_status__in=[
                SubTaskApproval.ApprovalStatus.SUBMITTED,
                SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
            ]
        ).order_by('step_order')

        tracker.current_review_step = pending.first().step_order if pending.exists() else 0



class FieldAgentResubmitStepView(APIView):
    """
    Field agent endpoint to resubmit a corrected step.
    Called from mobile app after fixing corrections.
    """
    permission_classes = []
    
    @transaction.atomic
    def post(self, request):
        try:
            tracker_id = request.data.get('tracker_id')
            step_order = request.data.get('step_order')
            
            if not tracker_id or not step_order:
                return HttpResponse.BadRequest("tracker_id and step_order are required")
            
            tracker = get_object_or_404(SubTaskTracker, id=tracker_id)
            
            # Verify user is assigned to this subtask
            if tracker.subtask.assign_to != request.user:
                return HttpResponse.Forbidden("You are not assigned to this subtask")
            
            # Get the step approval
            step_approval = get_object_or_404(
                SubTaskApproval,
                subtask_tracker=tracker,
                step_order=step_order
            )
            
            # Verify step needs correction
            if step_approval.approval_status != SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED:
                return HttpResponse.BadRequest(
                    f"Step {step_order} is not marked for correction"
                )
            
            # Update correction status
            pending_corrections = step_approval.corrections.filter(
                status=StepCorrection.CorrectionStatus.PENDING_CORRECTION
            )
            pending_corrections.update(
                status=StepCorrection.CorrectionStatus.RESUBMITTED,
                resubmitted_at=timezone.now()
            )
            
            # Update step approval status
            step_approval.approval_status = SubTaskApproval.ApprovalStatus.SUBMITTED
            step_approval.save()
            
            # Check if all corrections are resubmitted
            still_pending = tracker.step_approvals.filter(
                approval_status=SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
            ).count()
            
            if still_pending == 0:
                # All corrections fixed - send back to ops
                tracker.flow_status = FLOW_STATUS.SENT_TO_CENTRAL_OPS.value
                
                # Reset review step to earliest resubmitted step
                earliest_resubmitted = tracker.step_approvals.filter(
                    approval_status=SubTaskApproval.ApprovalStatus.SUBMITTED
                ).order_by('step_order').first()
                
                if earliest_resubmitted:
                    tracker.current_review_step = earliest_resubmitted.step_order
                
                tracker.save()
            
            serializer = SubTaskTrackerApprovalDetailSerializer(tracker)
            return HttpResponse.Success({
                'message': f'Step {step_order} resubmitted successfully',
                'tracker': serializer.data
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))


class GetSubTaskTrackerApprovalDetailView(APIView):
    """
    Get detailed approval status for a subtask tracker.
    Used by mobile app to show step-wise approval status and corrections.
    """
    permission_classes = []
    
    def get(self, request):
        try:
            tracker_id = request.query_params.get('tracker_id')
            
            if not tracker_id:
                return HttpResponse.BadRequest("tracker_id is required")
            
            tracker = get_object_or_404(SubTaskTracker, id=tracker_id)
            
            serializer = SubTaskTrackerApprovalDetailSerializer(tracker)
            return HttpResponse.Success({'tracker': serializer.data})
            
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))


class GetCorrectionReasonsView(APIView):
    """
    Get available correction reasons for a specific flow and step.
    Used by Central Ops UI to populate dropdown.
    """
    permission_classes = []
    
    def get(self, request):
        try:
            flow_description = request.query_params.get('flow_description')
            step_order = request.query_params.get('step_order')
            
            if not flow_description or not step_order:
                return HttpResponse.BadRequest(
                    "flow_description and step_order are required"
                )
            
            step_order = int(step_order)
            reasons = CORRECTION_REASONS.get_reasons_for_flow(
                flow_description, 
                step_order
            )
            
            return HttpResponse.Success({
                'flow_description': flow_description,
                'step_order': step_order,
                'reasons': reasons
            })
            
        except ValueError:
            return HttpResponse.BadRequest("step_order must be an integer")
        except Exception as e:
            return HttpResponse.InternalServerError(str(e))
        
class FinalTrackerApprovalView(APIView):
    """
    FINAL APPROVAL API - Tracker Level Decision
    """
    permission_classes = []
    
    @transaction.atomic
    def post(self, request):
        try:
            user = request.user  # Safe - IsAuthenticated passed
            
            serializer = FinalApprovalSerializer(data=request.data)
            if not serializer.is_valid():
                return HttpResponse.BadRequest(serializer.errors)
            
            data = serializer.validated_data
            tracker = get_object_or_404(SubTaskTracker, id=data['tracker_id'])
            action = data['action']
            comment = data.get('comment', '')
            
            # Get ALL pending/reviewable steps
            #  VALIDATION: All steps must be REVIEWED before final decision
            not_reviewed_steps = tracker.step_approvals.filter(
                approval_status__in=[
                    SubTaskApproval.ApprovalStatus.SUBMITTED,
                    SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
                ]
            ).order_by('step_order')

            if not_reviewed_steps.exists():
                step_numbers = list(
                    not_reviewed_steps.values_list('step_order', flat=True)
                )
                return HttpResponse.BadRequest(
                    f"Final approval blocked. "
                    f"Steps not reviewed yet: {step_numbers}. "
                    f"Please complete step-wise Central Ops review first."
                )

            #  Only REVIEWED steps are eligible for final action
            pending_steps = tracker.step_approvals.filter(
                approval_status=SubTaskApproval.ApprovalStatus.REVIEWED
            ).order_by('step_order')

            if not pending_steps.exists():
                return HttpResponse.BadRequest(
                    "No reviewed steps available for final approval."
                )


            
            results = []
            
            if action == 'APPROVE':
                for step_approval in pending_steps:
                    self._approve_step(step_approval, tracker, user)
                    results.append({
                        'step_order': step_approval.step_order,
                        'status': 'approved',
                        'message': f"Step {step_approval.step_order} approved (FINAL)"
                    })
                self._complete_flow(tracker, user)
                
            elif action == 'REJECT':
                tracker.flow_status = FLOW_STATUS.REJECTED_BY_CENTRAL_OPS.value
                tracker.central_ops_status = "REJECTED"
                tracker.central_ops_user = user
                tracker.current_review_step = 0
                tracker.save()

                results.append({
                    'status': 'rejected',
                    'message': 'Tracker rejected at final approval level'
                })

                
            elif action == 'PARTIAL_APPROVE':
                total_pending = pending_steps.count()
                approve_count = max(1, (total_pending * 2) // 3 + 1)
                steps_list = list(pending_steps)
                
                for i, step_approval in enumerate(steps_list):
                    if i < approve_count:
                        self._approve_step(step_approval, tracker, user)
                        results.append({
                            'step_order': step_approval.step_order,
                            'status': 'approved',
                            'message': f"Step {step_approval.step_order} approved (PARTIAL)"
                        })
                    else:
                        self._send_back_step(step_approval, tracker, "PARTIAL_REJECTION", "Partial rejection", user)
                        results.append({
                            'step_order': step_approval.step_order,
                            'status': 'rejected',
                            'message': f"Step {step_approval.step_order} rejected (PARTIAL)"
                        })
            
            tracker_serializer = SubTaskTrackerApprovalDetailSerializer(tracker)
            
            return HttpResponse.Success({
                'message': f'Final decision applied: {action} ({len(results)} steps processed)',
                'action': action,
                'user_id': 'ops_user',  # ✅ NO user.id!
                'results': results,
                'tracker': tracker_serializer.data
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return HttpResponse.InternalServerError(str(e))

    def _approve_step(self, step_approval, tracker, user):
        step_approval.approval_status = SubTaskApproval.ApprovalStatus.APPROVED
        step_approval.approved_by = user
        step_approval.approved_at = timezone.now()
        step_approval.save()
        
        step_approval.corrections.filter(
            status=StepCorrection.CorrectionStatus.RESUBMITTED
        ).update(status=StepCorrection.CorrectionStatus.RESOLVED, resolved_at=timezone.now())

    def _send_back_step(self, step_approval, tracker, reason, comment, user):
        step_approval.approval_status = SubTaskApproval.ApprovalStatus.CORRECTION_NEEDED
        step_approval.save()
        
        StepCorrection.objects.create(
            flow_step_approval=step_approval,
            reason=reason,
            comment=comment,  # ✅ NO user.id here!
            corrected_by=user,
            status=StepCorrection.CorrectionStatus.PENDING_CORRECTION
        )
        
        tracker.flow_status = FLOW_STATUS.SENT_BACK_BY_CENTRAL_OPS.value
        tracker.central_ops_status = "REJECTED"
        tracker.central_ops_user = user
        tracker.save()

    def _complete_flow(self, tracker, user):
        tracker.all_steps_approved = True
        flow_desc = tracker.flow.flow_description
        
        if flow_desc == "Location Verification":
            tracker.flow_status = FLOW_STATUS.LOCATION_VERIFICATION_VERIFIED_BY_CENTRAL_OPS.value
        elif flow_desc == "Location Re-Verification":
            tracker.flow_status = FLOW_STATUS.LOCATION_RE_VERIFICATION_VERIFIED_BY_CENTRAL_OPS.value
        elif flow_desc == "Upload KYC Document":
            tracker.flow_status = FLOW_STATUS.UPLOAD_KYC_DOCUMENT_VERIFIED_BY_CENTRAL_OPS.value
        elif flow_desc == "Lead Generation":
            tracker.flow_status = FLOW_STATUS.LEAD_GENERATION_COMPLETED.value
        else:
            tracker.flow_status = FLOW_STATUS.VERIFIED_BY_CENTRAL_OPS.value
        
        tracker.progress = 100
        tracker.central_ops_status = "APPROVED"
        tracker.central_ops_user = user
        tracker.current_review_step = 0
        
        # ✅ Reward logic - SAFE version
        # ✅ Reward logic - FINAL approval only
        try:
            if tracker.reward and tracker.reward > 0:
                subtask = tracker.subtask
                agent = subtask.assign_to if subtask else None

                if not agent:
                    raise ValueError("Assigned agent not found for reward")

                from users.models import UserReward

                description_text = f"Reward for completing {tracker.flow.flow_description}"
                today = timezone.now().date()

                exists = UserReward.objects.filter(
                    user=agent,
                    description=description_text,
                    amount=tracker.reward,
                    created_at__date=today
                ).exists()

                if not exists:
                    UserReward.objects.create(
                        user=agent,
                        amount=tracker.reward,
                        description=description_text
                    )

        except Exception as e:
            print("REWARD ERROR:", str(e))

        tracker.save()

        
        tracker.save()
