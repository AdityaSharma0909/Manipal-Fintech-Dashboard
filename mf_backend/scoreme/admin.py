from django.contrib import admin
from scoreme.models import ScoreMeBankAnalysis

# Register your models here.
@admin.register(ScoreMeBankAnalysis)
class ScoreMeBankAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'application',
        'reference_id',
        'json_url',
        'excel_url',
        'webhook_response'
    )
    search_fields = ('reference_id', 'application__application_id')