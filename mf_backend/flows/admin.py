from django.contrib import admin
from .models import Flow, FlowStep

class FlowStepInline(admin.TabularInline):
    model = FlowStep
    extra = 1

@admin.register(Flow)
class FlowAdmin(admin.ModelAdmin):
    list_display = ('flow_id', 'flow_description', 'category', 'is_active')
    inlines = [FlowStepInline]
