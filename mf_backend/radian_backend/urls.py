"""radian_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path ,include
from users.views.CustomTokenView import CustomTokenView
from django.conf.urls.static import static
from django.conf import settings
from .views import LoanCalculatorByAmount, LoanCalculatorByAsset, RadianProductView, GenerateOpenLeadsView, GoldPricesView, GoldValue, CheckUpdateView, LegalDocumentsView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic.base import RedirectView

import os


urlpatterns = [
    path('', RedirectView.as_view(url='/api/docs/', permanent=False), name='root-redirect'),
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    re_path(r"authenticate/token/$", CustomTokenView.as_view(), name="token"),
    path('user/', include('users.urls')),
    path('account/', include('account.urls')),
    path('application/',include('application.urls')),
    path('lead/', include('lead.urls')),
    path('asset/', include('asset.urls')),
    path('document/', include('document.urls')),
    path('product/', include('product.urls')),
    path('loan/', include('loan.urls')),
    path('disbursements/', include('disbursements.urls')),
    path('lender/', include('lender.urls')),
    path('branch/', include('branch.urls')),
    path('gold_prices/', GoldPricesView.as_view()),
    path('radian_products/all/', RadianProductView.as_view()),
    path('generate_open_leads/', GenerateOpenLeadsView.as_view()),
    path('gold_value/', GoldValue.as_view()),
    path('gold_loan_calculator_by_amount/', LoanCalculatorByAmount.as_view()),
    path('gold_loan_calculator_by_asset/', LoanCalculatorByAsset.as_view()),
    path('core/', include('core.urls')),
    path('federal/',include('federal.urls')),
    path('payment/',include('payment.urls')),
    path('credit/',include('credit_status.urls')),
    path('reference_pd/',include('reference_pd.urls')),
    path('tele/', include('tele_verification.urls')),
    path('scoreme/',include('scoreme.urls')),
    path('cibil/', include('cibil_score.urls')),
    path('flow/', include('flows.urls')),
    path('task/', include('tasks.urls')),
    path('zoop/',include('zoop.urls')),
    path('atlas-ocr/', include('atlas_ocr.urls')),
    path('api/v2/atlas-ocr/', include('atlas_ocr.urls')),
    path('leegality/',include('Leegality.urls')),
    path('api/v2/onboarding/', include('onboarding_v2.urls')),
    path('api/v2/check-update/', CheckUpdateView.as_view()),
    path('api/v2/legal-documents/', LegalDocumentsView.as_view()),
    path('insurance/',include('insurance.coverfox.urls') ),
    path('api/v2/crif/', include('crif_bureau.urls')),
    # ── Analytics Dashboard (API-key secured, read-only) ──
    path('dashboard/', include('dashboard.urls')),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
   + static('static_assets/', document_root=os.path.join(settings.BASE_DIR, 'assets'))
