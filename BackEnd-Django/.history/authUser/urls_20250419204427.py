from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)
from .views import RegisterView,RegisterVerifyView ,LoginRequestView,CurrentUserView
from .views import PasswordChangeView,PasswordResetRequestView,PasswordResetView
from .views import PinChangeView,PinResetRequestView,PinResetView,PasswordForgetRequestView,PasswordForgetView

urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('register/verify-email/',RegisterVerifyView.as_view(),name='register-verify'),
    
    path('loginRequest/',LoginRequestView.as_view(),name='login-requests'),
    path('current-user/',CurrentUserView.as_view(),name='get-current-user'),
    
    path('password-change/',PasswordChangeView.as_view(),name='password-change'),
    path('password-reset-request/',PasswordResetRequestView.as_view(),name='password-reset-request'),
    path('password-reset/',PasswordResetView.as_view(),name='password-reset'),
    
    path('password-forget-request/',PasswordForgetRequestView.as_view(),name='password-forget-request'),
    path('password-forget/',PasswordForgetView.as_view(),name='password-forget'),
    
    path('pin-change/',PinChangeView.as_view(),name='pin-change'),
    path('pin-reset-request/',PinResetRequestView.as_view(),name='pin-reset-request'),
    path('pin-reset/',PinResetView.as_view(),name='pin-reset'),
    
    # from rest  frame work 
    path('api/token/', TokenObtainPairView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
]

# for login 
#     fields
#         username_field (required)
#         password (required)
#         email_verification_code (optional)
#         send to  ENDPOINT =>>>>> login-request
    
        
# for register 
#     fields 
#         phone_number
#         username 
#         email 
#         password 
#         password1
#         refarrel_code
#          if email or phone number is already found but email is not verifie d so we need to
#          confirm that email using otp 
#          and we weill be redirected to login page