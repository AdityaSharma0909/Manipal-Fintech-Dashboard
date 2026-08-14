from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('third-party-lender/', include('third_party_lender.urls')),
]
