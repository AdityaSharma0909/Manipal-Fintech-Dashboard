from django.urls import path 
from .views.disbursement import DisbursementView,DisbursementAllView
from .views.export_disbusrement_data import ExportDisbursementView
from .views.import_disbursement import ExcelImportView
from .views.upload_utr_no import DisbursementUpdateView
urlpatterns =[
    path("",DisbursementView.as_view()),
    path("all/",DisbursementAllView.as_view()),
    path("export/",ExportDisbursementView.as_view()),
    path("import/",ExcelImportView.as_view()),
    path("upload/",DisbursementUpdateView.as_view())
    
]