from django.urls import path
from .views import *

urlpatterns = [
    # Define your URL patterns here
    #------------------school--------------------------
    # GET tested ,PUT tested , POST for DELETE is Tested
    path('school-detail/<uuid:school_id>/', DirectorSchoolDetailView.as_view(), name='school-detail'), #Tested
    
    #------------------student--------------------------
    
    path('add-student/', DirectorStudentView.as_view(),  name='add-student'),
    path('all-students/<uuid:school_id>/', DirectorAllStudentsView.as_view(), name='all-student'), #Tested
    
    path('get-student/<uuid:student_id>/', DirectorStudentView.as_view(), name='get-student'), #Tested
    path('update-student/<str:student_id>/', DirectorStudentView.as_view(), name='update-student'),
    path('manage-student/<str:student_id>/', DirectorStudentAdministrationView.as_view(), name='manage-student'),
    
   ]