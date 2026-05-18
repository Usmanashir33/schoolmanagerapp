from django.urls import path 

from . views import  *

urlpatterns = [
    # Define your URL patterns here  
    
    path('register-new-school/', SchoolAndDirectorCreateView.as_view(), name='create-school'), #tested
    
    path('template/<str:school_id>/', SchoolTemplateView.as_view(), name='newTemplate'), #tested
    
    path('template/<str:school_id>/<str:template_id>/', SchoolTemplateView.as_view(), name='get&PutTemplate'),
    path('template/<str:school_id>/<str:template_id>/<str:pin>/', SchoolTemplateView.as_view(), name='deleteTemplate'),
    path('finance/create/', SchoolFinanceView.as_view(), name='createFinanceData'),
    path('finance/update/<str:acc_id>/', SchoolFinanceView.as_view(), name='updateFinanceData'),
    path('finance/delete/<str:school_id>/<str:acc_id>/<str:pin>/', SchoolFinanceView.as_view(), name='deleteFinanceData'),
    
]  