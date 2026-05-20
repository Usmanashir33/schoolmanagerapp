from django.urls import path

from . views import *

urlpatterns = [
    # Define your URL patterns here
    #------------------ staff --------------------------
    path('add-staff/',                   StaffCreateUpdateView.as_view(),  name='add-staff'),#Tested
    
    path('get-staff/<uuid:staff_id>/',   StaffCreateUpdateView.as_view(), name='get-staff'), #Tested
    path('update-staff/<str:staff_id>/', StaffCreateUpdateView.as_view(), name='update-staff'),#Tested
    
    path('all-staffs/<uuid:school_id>/', AllStaffsView.as_view(), name='all-staff'), 
    path('search/staff/<str:searchQuery>/',FilterStaffView.as_view(),  name='search-staff'),#Tested
    path('manage-staff/<str:staff_id>/<str:request_action>/', StaffAdministrationView.as_view(), name='manage-staff'),#tasted
    
]