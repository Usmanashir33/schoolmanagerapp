from django.urls import path

from .views import *

urlpatterns = [
    #------------------student--------------------------
    path('all-students/<uuid:school_id>/',  AllStudentsView.as_view(), name='all-student'),
    path('all-students/<uuid:school_id>/<str:class_id>/',  ClassCurrentStudentsListView.as_view(), name='all-class-current-students'),
    path('add-student/',                StudentDetailView.as_view(),  name='add-student'),#Tested
    path('search/<uuid:school_id>/<str:searchQuery>/',  FilterStudentDetailView.as_view(), name='search-student'), #Tested
    path('details/<uuid:school_id>/<uuid:student_id>/',  StudentDetailView.as_view(), name='get-student'), #Tested
    path('update-student/<str:student_id>/',StudentDetailView.as_view(), name='update-student'),#Tested
    path('manage-student/<str:student_id>/<str:request_action>/', StudentAdministrationView.as_view(), name='manage-student'),#tasted
    
]
