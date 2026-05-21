from django.urls import path 

from . views import  *

urlpatterns = [
    # Define your URL patterns here  
    
    path('register-new-school/', SchoolAndDirectorCreateView.as_view(), name='create-school'), #tested
    
    path('role/create/', SchoolRoleView.as_view(), name='role'),
    path('role/update/<str:role_id>/', SchoolRoleView.as_view(), name='update-role'),
    path('role/delete/<str:role_id>/<str:pin>/', SchoolRoleView.as_view(), name='delete-role'),
    
    path('permission/create/', SchoolPermsionView.as_view(), name='permission'),
    path('permission/update/<str:perm_id>/', SchoolPermsionView.as_view(), name='update-permission'),
    path('permission/delete/<str:perm_id>/<str:pin>/', SchoolPermsionView.as_view(), name='delete-permission'),
    
    
    
    path('template/<str:school_id>/', SchoolTemplateView.as_view(), name='newTemplate'), #tested
    
    path('template/<str:school_id>/<str:template_id>/', SchoolTemplateView.as_view(), name='get&PutTemplate'),
    path('template/<str:school_id>/<str:template_id>/<str:pin>/', SchoolTemplateView.as_view(), name='deleteTemplate'),
    path('finance/create/', SchoolFinanceView.as_view(), name='createFinanceData'),
    path('finance/update/<str:acc_id>/', SchoolFinanceView.as_view(), name='updateFinanceData'),
    path('finance/delete/<str:school_id>/<str:acc_id>/<str:pin>/', SchoolFinanceView.as_view(), name='deleteFinanceData'),
    
]  