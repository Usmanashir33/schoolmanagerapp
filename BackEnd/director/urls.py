from django.urls import path
from .views import *

urlpatterns = [
    # Define your URL patterns here
    #------------------school--------------------------
    # GET tested ,PUT tested , POST for DELETE is Tested
    path('school-detail/<uuid:school_id>/', DirectorSchoolDetailView.as_view(), name='school-detail'), #Tested
     
    #------------------student--------------------------
    path('all-students/<uuid:school_id>/', DirectorAllStudentsView.as_view(), name='all-student'), #Tested
    path('add-student/', DirectorStudentDetailView.as_view(),  name='add-student'),#Tested
    path('get-student/<uuid:student_id>/', DirectorStudentDetailView.as_view(), name='get-student'), #Tested
    path('update-student/<str:student_id>/', DirectorStudentDetailView.as_view(), name='update-student'),#Tested
    path('manage-student/<str:student_id>/', DirectorStudentAdministrationView.as_view(), name='manage-student'),
    
    #------------------Teacher--------------------------
    path('add-teacher/', DirectorTeacherDetailView.as_view(),  name='add-teacher'),#Tested
    path('all-teachers/<uuid:school_id>/', DirectorAllTeachersView.as_view(), name='all-teacher'), 
    path('get-teacher/<uuid:teacher_id>/', DirectorTeacherDetailView.as_view(), name='get-teacher'),#Tested 
    path('update-teacher/<str:teacher_id>/', DirectorTeacherDetailView.as_view(), name='update-teacher'),#Tested
    path('manage-teacher/<str:teacher_id>/', DirectorTeacherAdministrationView.as_view(), name='manage-teacher'),
    
    #------------------Staff--------------------------
    path('add-staff/', DirectorStaffView.as_view(),  name='add-staff'),#Tested
    path('all-staffs/<uuid:school_id>/', DirectorAllStaffsView.as_view(), name='all-staff'), 
    path('get-staff/<uuid:staff_id>/', DirectorStaffView.as_view(), name='get-staff'), #Tested
    path('update-staff/<str:staff_id>/', DirectorStaffView.as_view(), name='update-staff'),#Tested
    path('manage-staff/<str:staff_id>/', DirectorStaffAdministrationView.as_view(), name='manage-staff'),
    
    #--------------------------------ACADEMICS----------------------------
    path('academics/<str:academic_item>/', DirectorAcademicView.as_view(), name='academics'),
    path('academics/<str:academic_item>/<str:item_id>/', DirectorAcademicView.as_view(), name='academics-update'),
    
   ]