from django.urls import path 

from . views import  *

urlpatterns = [
    # Define your URL patterns here  
    
    path('register-new-school/', SchoolAndDirectorCreateView.as_view(), name='create-school'), #tested done 
    path('school-detail/director/<uuid:school_id>/', DirectorSchoolDetailView.as_view(), name='school-detail-director'), #Tested
    path('school-detail/<uuid:school_id>/', SchoolDetailView.as_view(), name='school-detail'),  #Done
    path('config/', SchoolConfigView.as_view(), name='school-config') ,  #Done
    
    path('userlogs/<uuid:school_id>/', AllUserLogsView.as_view(), name='userlogs'), #tested done
    
    path('role/create/', SchoolRoleView.as_view(), name='role'), #Done
    path('role/update/<str:role_id>/', SchoolRoleView.as_view(), name='update-role'), #Done
    path('role/delete/<uuid:school_id>/<str:role_id>/<str:pin>/', SchoolRoleView.as_view(), name='delete-role'), #Done
    
    path('permission/create/', SchoolPermsionView.as_view(), name='permission'), #Done
    path('permission/update/<str:perm_id>/', SchoolPermsionView.as_view(), name='update-permission'), #Done
    path('permission/delete/<str:perm_id>/<str:pin>/', SchoolPermsionView.as_view(), name='delete-permission'),
    
    path('finance/create/', SchoolFinanceView.as_view(), name='createFinanceData'), #Done
    path('finance/update/<str:acc_id>/', SchoolFinanceView.as_view(), name='updateFinanceData'),#Done
    path('finance/delete/<str:school_id>/<str:acc_id>/<str:pin>/', SchoolFinanceView.as_view(), name='deleteFinanceData'),#Done
    
    
    path('template/<str:school_id>/', SchoolTemplateView.as_view(), name='newTemplate'), #tested
    path('template/<str:school_id>/<str:template_id>/', SchoolTemplateView.as_view(), name='get&PutTemplate'),
    path('template/<str:school_id>/<str:template_id>/<str:pin>/', SchoolTemplateView.as_view(), name='deleteTemplate'),
    
]  