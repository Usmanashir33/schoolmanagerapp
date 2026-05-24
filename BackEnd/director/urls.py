from django.urls import path

# from .academic_views import *
from academics.views import *
from .school_views import *
from .director_views import *

urlpatterns = [
    # Define your URL patterns here
    #------------------Director--------------------------
    path('update/', DirectorDetailView.as_view(), name='update-detail'), #Tested
    path('security-settings/<uuid:school_id>/', DirectorSettingsView.as_view(), name='security-settings'), #Tested
    
    #------------------school--------------------------
    # GET tested ,PUT tested , POST for DELETE is Tested
    path('school-detail/<uuid:school_id>/', DirectorSchoolDetailView.as_view(), name='school-detail'), #Tested
    path('academic-settings/<uuid:school_id>/', DirectorAcademicSettingsView.as_view(), name='school-detail'), #Tested
      
    
    # #------------------Staff--------------------------
    # path('all-staffs/<uuid:school_id>/', DirectorAllStaffsView.as_view(), name='all-staff'), 
    # path('search/staff/<str:searchQuery>/',DirectorFilterStaffView.as_view(),  name='search-staff'),#Tested
    # path('add-staff/',                   DirectorStaffView.as_view(),  name='add-staff'),#Tested
    # path('get-staff/<uuid:staff_id>/',   DirectorStaffView.as_view(), name='get-staff'), #Tested
    # path('update-staff/<str:staff_id>/', DirectorStaffView.as_view(), name='update-staff'),#Tested
    # path('manage-staff/<str:staff_id>/<str:request_action>/', DirectorStaffAdministrationView.as_view(), name='manage-staff'),#tasted
    
    # #--------------------------------ACADEMICS----------------------------
    # path('academics/<str:academic_item>/',               DirectorAcademicView.as_view(), name='academics'), #tasted
    # path('academics/<str:academic_item>/<str:item_id>/', DirectorAcademicView.as_view(), name='academics-update'),#tasted
    # path('class/transfer/', DirectorClassTransferView.as_view(), name='class-transfer') ,
    # path('class/promotion/', DirectorClassPromotionView.as_view(), name='class-promotion') ,
    
   ]