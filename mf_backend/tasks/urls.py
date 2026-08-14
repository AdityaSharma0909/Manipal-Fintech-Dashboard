# task/urls.py
from django.urls import path
from .view.subtask import (
    SubTaskView , AssignSubTaskAPIView,ReassignSubTaskAPIView,
    SubTaskSearchAPIView,ActiveUsersDropdownAPIView, SubTaskExportAPIView
)
from .view.subtask_tracker import SubTaskTrackerView , PanOtpSendView, PanOtpVerifyView
from .view.task import TaskView, TaskCloseView
from tasks.view.task_dashboard import TaskDashboardHomeView, TaskEarningsView, TaskDisbursementView, RHDashboardView
from tasks.view.approval import (
    CentralOpsReviewView,
    FieldAgentResubmitStepView,
    GetSubTaskTrackerApprovalDetailView,
    GetCorrectionReasonsView,FinalTrackerApprovalView,
    
    
)
from .view.subtask import SubTaskDeclineAPIView
urlpatterns = [
    path('', TaskView.as_view(), name='taskView'),
    path('subtasks/', SubTaskView.as_view(), name='subtaskView'),
    path('assign_subtasks/', AssignSubTaskAPIView.as_view(), name='assignSubTaskAPIView'),
    path("subtasks/reassign/", ReassignSubTaskAPIView.as_view(),name='ReassignSubTaskAPIView'),
    path("subtasks/search/", SubTaskSearchAPIView.as_view(),name='SubTaskSearchAPIView'),
    path("subtasks/active-users/", ActiveUsersDropdownAPIView.as_view(),name='active-users'),
    path('subtasks/export/', SubTaskExportAPIView.as_view(), name='subtask-export'),


    path('subtask_tracker/', SubTaskTrackerView.as_view(), name='subTaskTrackerView'),
    path('pan_otp_send/', PanOtpSendView.as_view(), name='panOtpSendView'),
    path('pan_otp_verify/', PanOtpVerifyView.as_view(), name='panOtpVerifyView'),
    path('task_dashboard_view/', TaskDashboardHomeView.as_view(), name='task_dashboard_view'),
    path('rh_dashboard_view/', RHDashboardView.as_view(), name='rh_dashboard_view'),
    path('task_dashboard_earnings/', TaskEarningsView.as_view(), name='task_dashboard_earnings'),
    path('task_dashboard_disbursement/', TaskDisbursementView.as_view(), name='task_dashboard_disbursement'),
    path('task/close/', TaskCloseView.as_view(), name='task-close'),
    
    # Flow Approval URLs
    path('approval/review/', CentralOpsReviewView.as_view(), name='central-ops-review'),
    path('approval/resubmit/', FieldAgentResubmitStepView.as_view(), name='field-agent-resubmit'),
    path('approval/detail/', GetSubTaskTrackerApprovalDetailView.as_view(), name='approval-detail'),
    path('approval/correction-reasons/', GetCorrectionReasonsView.as_view(), name='correction-reasons'),
    path('approval/final-decision/', FinalTrackerApprovalView.as_view(), name='final-tracker-approval'),
    path('subtasks/decline/', SubTaskDeclineAPIView.as_view(), name='subtask-decline'),
]
