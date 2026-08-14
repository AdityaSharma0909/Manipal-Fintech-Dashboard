from django.urls import path,re_path ,include
from .views.FederalApplicationEligibility import EligibilityView
from .views.FederalCustomerCreation import FederalCustomerCreation,SolidMapping
from .views.FederalConsentView import ConsentView,AadharVerificationView
from .views.FederalGoldLoanView import GLOpenView
from .views.FederalApplication import FederalApplication


urlpatterns =[
    path("submitConsent/",ConsentView.as_view()),
    path("ekyc/",AadharVerificationView.as_view()),
    path("checkEligibility/",EligibilityView.as_view()),
    path("createCustomer/",FederalCustomerCreation.as_view()),
    path("openGLAccount/",GLOpenView.as_view()),
    # path("validateGLAccount/",GLValidateView.as_view()),
    path("getSolid/",SolidMapping.as_view()),
    path("",FederalApplication.as_view()),
]