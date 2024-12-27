from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .view.user_account_management import RegisterView, LoginView, LoginViewWithKeys,VerifyOTPView, UpdateTimezoneView
from .view.bank_account_management import BankAccountView, BatchAccountCreationView
from .view.transaction import DepositView, WithdrawView, TransferView, TransactionHistoryView, ExternalTransferView, TransactionHistoryCachedView
from .view.user_role_management import RoleView, UserRoleView, PermissionView
from .view.reports import AdminReportView

urlpatterns = [

    # Swagger UI    

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # User Auth    
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('loginwithkeys/', LoginViewWithKeys.as_view(), name='login-with-keys'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('users/update-timezone/', UpdateTimezoneView.as_view(), name='update-timezone'),

    #Bank Account Creations
    path('accounts/', BankAccountView.as_view(), name='bank-account'),
    path('accounts/batch-create/', BatchAccountCreationView.as_view(), name='batch-account-create'),    

    #Transactions
    path('transactions/deposit/', DepositView.as_view(), name='deposit'),
    path('transactions/withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('transactions/transfer/', TransferView.as_view(), name='transfer'),
    path('transactions/history/', TransactionHistoryView.as_view(), name='transaction-history'),
    path('transactions/external-transfer/', ExternalTransferView.as_view(), name='external-transfer'),

    #Role and Permission 
    path('roles/', RoleView.as_view(), name='roles'),
    path('roles/assign/', UserRoleView.as_view(), name='assign-role'),
    path('permissions/', PermissionView.as_view(), name='permissions'),

    #Redis Cached
    path('transactions/history/cached/', TransactionHistoryCachedView.as_view(), name='transaction-history'),

    #Admin ReportView
    path('admin/reports/', AdminReportView.as_view(), name='admin-reports'),
]

