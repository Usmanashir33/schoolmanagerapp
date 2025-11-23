from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

from .views import RegisterView,RegisterVerifyView ,LoginRequestView,CurrentUserView
from .views import PasswordChangeView,PasswordResetView,SearchUserView,ProfileUpdateView
from .views import PasswordForgetView,VerifyWithEmailOtp,RetriveOtpView
# from .views import PinChangeView,ManageUserLogin

urlpatterns = [
    
    path('email-verif-code/',VerifyWithEmailOtp.as_view(),name='email-verification'), 
    path('resend-otp/',RetriveOtpView.as_view(),name='resend-otp'), 
    
    # register and login view 
    path('register/',RegisterView.as_view(),name='register'),  
    path('register/verify-email/',RegisterVerifyView.as_view(),name='register-verify'),
    path('loginRequest/',LoginRequestView.as_view(),name='login-requests'),
    
    # password end points 
    path('password-change/',PasswordChangeView.as_view(),name='password-change'),
    path('password-reset/',PasswordResetView.as_view(),name='password-reset'),
    path('password-forget/',PasswordForgetView.as_view(),name='password-forget'),
    
    # pin endpoints 
    # path('pin-change/',PinChangeView.as_view(),name='pin-change'),
    # path('manage-user-login/',ManageUserLogin.as_view(),name='manage-user-login'),
    
    path('current-user/',CurrentUserView.as_view(),name='get-current-user'),
    path("search-user/",SearchUserView.as_view(),name='search-user'),
    path('update-profile/',ProfileUpdateView.as_view(),name='update-profile'),
    
    # from rest  frame work 
    path('api/login/', TokenObtainPairView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]