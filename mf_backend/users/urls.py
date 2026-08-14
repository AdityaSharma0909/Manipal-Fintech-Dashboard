"""All user & auth related endpionts goes here"""

from django.urls import path, include

from .views.UserView import GenerateOtpView, VerifyOtpView, LoginView, PasswordChangeView , UserByIdView
from .views.UserViewCustomer import CustomerGenerateOtpView, CustomerVerifyOtpView
from .views.AddresView import AddressesView 
from .views.FCMView import UserDeviceView
from .views.Registration import RegistrationView,BranchManager,AllUsers ,UserAll, UserByRole, TestView
from .views.TimeStamp import TimeStampView, TimeStampExportView, TimeStampDownloadExcelView
from .views.all_employess import AllEmployeeView, ApplicationPerEmployee, SalesOfficerBulkUploadView
from .views.export_user_data import ExportUserView
from .search import UserSearchAPI
from .views.agent import AgentGenerateOtpView, AgentVerifyOtpView , AgentView
from .views.sales_officer import SalesOfficerGenerateOtpView, SalesOfficerVerifyOtpView, SalesOfficerSetNewPasswordView
from .views.ForgotPassword import ForgotPasswordRequestView, ForgotPasswordVerifyView, ForgotPasswordResetView, ForgotPasswordUpdateView, RememberMeView
from .views.User_reports import UserReportAPIView, AttendanceReportAPIView

urlpatterns = [
    # path('', LoginView.as_view(), name='login'),
    path(r'generateOtp/', GenerateOtpView.as_view()),
    path(r'verifyOtp/',VerifyOtpView.as_view()),
    path(r'customer/generateOtp/', CustomerGenerateOtpView.as_view()),
    path(r'customer/verifyOtp/',CustomerVerifyOtpView.as_view()),
    path(r'address/', AddressesView.as_view()),
    path(r'login/', LoginView.as_view()),
    path(r'checkUser/', TimeStampView.as_view()),
    path(r'export-timestamp/', TimeStampExportView.as_view()),
    path(r'download-timestamp-excel/', TimeStampDownloadExcelView.as_view()),
    path(r"userDevice/", UserDeviceView.as_view()),
    path(r"register/", RegistrationView.as_view()),
    path(r"bm/", BranchManager.as_view()),
    path(r"all/", AllUsers.as_view()),
    path(r"getUser/", UserAll.as_view()),
    # path(r"notification/", FCMNotificationView.as_view()),
    path(r"by_role/", UserByRole.as_view()),
    path(r"test/", TestView.as_view()),
    path('reset-password/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path(r"password-update/", PasswordChangeView.as_view()),
    
    # Forgot Password Flow
    path(r'forgot-password/request/', ForgotPasswordRequestView.as_view()),
    path(r'forgot-password/verify/', ForgotPasswordVerifyView.as_view()),
    path(r'forgot-password/reset/', ForgotPasswordResetView.as_view()),
    path(r'forgot-password/update/', ForgotPasswordUpdateView.as_view()),
    path(r'remember-me/', RememberMeView.as_view()),

    path('employee', AllEmployeeView.as_view()),
    path('employee/bulk-upload/sales/sales-officer/', SalesOfficerBulkUploadView.as_view()),
    path('employee/applications', ApplicationPerEmployee.as_view()),
    path('export/',ExportUserView.as_view()),

    path('search/',UserSearchAPI.as_view()),
    path('agent/', AgentView.as_view()),
    path('agent/generateOtp/', AgentGenerateOtpView.as_view()),
    path('agent/verifyOtp/', AgentVerifyOtpView.as_view()),
    path('user_by_id/', UserByIdView.as_view()),
    path('sales_officer/generateOtp/', SalesOfficerGenerateOtpView.as_view()),
    path('sales_officer/verifyOtp/', SalesOfficerVerifyOtpView.as_view()),  
    path('sales_officer/setNewPassword/', SalesOfficerSetNewPasswordView.as_view()),
    path('report/', UserReportAPIView.as_view()),
    path('report/attendance/', AttendanceReportAPIView.as_view()),
    # Force reload 3
]
