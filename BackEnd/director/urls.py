from django.urls import path
# from .views_combined import *

# from .student_views import *
from .teacher_views import *
from .staff_views import *
from .academic_views import *
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
      
    #------------------student--------------------------
    # path('all-students/<uuid:school_id>/',  DirectorAllStudentsView.as_view(), name='all-student'),
    # path('add-student/',                    DirectorStudentDetailView.as_view(),  name='add-student'),#Tested
    # path('search/student/<str:searchQuery>/',  DirectorFilterStudentDetailView.as_view(), name='search-student'), #Tested
    # path('get-student/<uuid:student_id>/',  DirectorStudentDetailView.as_view(), name='get-student'), #Tested
    # path('update-student/<str:student_id>/',DirectorStudentDetailView.as_view(), name='update-student'),#Tested
    # path('manage-student/<str:student_id>/<str:request_action>/', DirectorStudentAdministrationView.as_view(), name='manage-student'),#tasted
    
    # #------------------ Teacher --------------------------
    # path('add-teacher/',                      DirectorTeacherDetailView.as_view(),  name='add-teacher'),#Tested
    # path('all-teachers/<uuid:school_id>/',    DirectorAllTeachersView.as_view(), name='all-teacher'), 
    # path('search/teacher/<str:searchQuery>/', DirectorFilterTeacherDetailView.as_view(), name='search-teacher'),#Tested 
    # path('get-teacher/<uuid:teacher_id>/',    DirectorTeacherDetailView.as_view(), name='get-teacher'),#Tested 
    # path('update-teacher/<str:teacher_id>/',  DirectorTeacherDetailView.as_view(), name='update-teacher'),#Tested
    # path('manage-teacher/<str:teacher_id>/<str:request_action>/' ,DirectorTeacherAdministrationView.as_view(), name='manage-teacher'),#tasted
    # path('teacher-record/<str:teacher_id>/',  DirectorTeacherRecordView.as_view(), name='teacher-record-add'),
    # path('teacher-record/<str:teacher_id>/<str:report_action>/', DirectorTeacherRecordView.as_view(), name='teacher-record-update'),
    
    #------------------Staff--------------------------
    path('all-staffs/<uuid:school_id>/', DirectorAllStaffsView.as_view(), name='all-staff'), 
    path('search/staff/<str:searchQuery>/',DirectorFilterStaffView.as_view(),  name='search-staff'),#Tested
    path('add-staff/',                   DirectorStaffView.as_view(),  name='add-staff'),#Tested
    path('get-staff/<uuid:staff_id>/',   DirectorStaffView.as_view(), name='get-staff'), #Tested
    path('update-staff/<str:staff_id>/', DirectorStaffView.as_view(), name='update-staff'),#Tested
    path('manage-staff/<str:staff_id>/<str:request_action>/', DirectorStaffAdministrationView.as_view(), name='manage-staff'),#tasted
    
    #--------------------------------ACADEMICS----------------------------
    path('academics/<str:academic_item>/',               DirectorAcademicView.as_view(), name='academics'), #tasted
    path('academics/<str:academic_item>/<str:item_id>/', DirectorAcademicView.as_view(), name='academics-update'),#tasted
    path('class/transfer/', DirectorClassTransferView.as_view(), name='class-transfer') ,
    path('class/promotion/', DirectorClassPromotionView.as_view(), name='class-promotion') ,
    
   ]