from django.contrib import admin
from .models import Task, TaskFlow, SubTask, SubTaskTracker, SubTaskDocument, SubTaskApproval, StepCorrection

class TaskFlowInline(admin.TabularInline):
    model = TaskFlow
    extra = 1

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'task_summary', 'priority', 'total_reward_assigned')
    inlines = [TaskFlowInline]

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'contact_person_name', 'type_of_user', 'assign_to')
    search_fields = ['id']

@admin.register(TaskFlow)
class TaskFlowAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'flow', 'condition', 'reward', 'order')

@admin.register(SubTaskTracker)
class SubTaskTrackerAdmin(admin.ModelAdmin):
    list_display = ('id', 'subtask', 'flow', 'flow_status', 'created_by','created_at')

@admin.register(SubTaskDocument)
class SubTaskDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'document_flow', 'document_type', 'file_name', 'subtask', 'uploaded_by')


@admin.register(SubTaskApproval)
class SubTaskApprovalAdmin(admin.ModelAdmin):
    list_display = ('id', 'subtask_tracker', 'flow_step', 'approval_status', 'approved_by', 'approved_at')
    
@admin.register(StepCorrection)
class StepCorrectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'corrected_by', 'corrected_at')