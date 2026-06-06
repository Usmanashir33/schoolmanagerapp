from django.urls import path

from . views import *

urlpatterns = [
    # Define your URL patterns here
    #------------------ Teacher --------------------------
    path('add-teacher/',                      TeacherView.as_view(),  name='add-teacher'),#Tested
    path('update-teacher/<str:teacher_id>/',  TeacherView.as_view(), name='update-teacher'),#Tested
    path('details/<uuid:school_id>/<uuid:teacher_id>/',    TeacherView.as_view(), name='get-teacher-details'),#Tested 
    path('all-teachers/<uuid:school_id>/',    AllTeachersView.as_view(), name='all-teacher'), # Tasted
    path('all-teachers/<uuid:school_id>/<str:class_id>/',    ClassCurrentTeachersListView.as_view(), name='all-teacher'), 
    path('search/teacher/<uuid:school_id>/<str:searchQuery>/', FilterTeacherDetailView.as_view(), name='search-teacher'),#Tested 
    path('manage-teacher/<uuid:school_id>/<str:teacher_id>/<str:request_action>/' ,TeacherAdministrationView.as_view(), name='manage-teacher'),#tasted
    
    path('teacher-record/<str:teacher_id>/',  TeacherRecordView.as_view(), name='teacher-record-add'),
    path('teacher-record/<str:teacher_id>/<str:report_action>/', TeacherRecordView.as_view(), name='teacher-record-update'),
    
]