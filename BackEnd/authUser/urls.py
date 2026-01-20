from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,)

from .views import RetriveOrGenOTPView,RegisterVerifyView ,LoginRequestView,CurrentUserView
from .views import PasswordChangeView,SearchUserView,ProfileUpdateView
# from .views import PinChangeView,ManageUserLogin

urlpatterns = [
    # for generating new and retriving current otp 
    path('resend-otp/',RetriveOrGenOTPView.as_view(),name='resend-otp'),  #Tested
    path('register/verify-email/',RegisterVerifyView.as_view(),name='register-verify'),  #Tested
    path('loginRequest/',LoginRequestView.as_view(),name='login-requests') , #Tested
    
    # password end points 
    path('password-change/',PasswordChangeView.as_view(),name='password-change'), #Tasted
    
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