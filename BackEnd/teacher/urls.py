from django.urls import path

from . views import *

urlpatterns = [
    # Define your URL patterns here
    #------------------ Teacher --------------------------
    path('add-teacher/',                      TeacherCreateView.as_view(),  name='add-teacher'),#Tested
    path('update-teacher/<str:teacher_id>/',  TeacherCreateView.as_view(), name='update-teacher'),#Tested
    path('get-teacher/<uuid:teacher_id>/',    TeacherCreateView.as_view(), name='get-teacher'),#Tested 
    path('all-teachers/<uuid:school_id>/',    AllTeachersView.as_view(), name='all-teacher'), 
    path('all-teachers/<uuid:school_id>/<str:class_id>/',    ClassCurrentTeachersListView.as_view(), name='all-teacher'), 
    path('search/teacher/<uuid:school_id>/<str:searchQuery>/', FilterTeacherDetailView.as_view(), name='search-teacher'),#Tested 
    path('manage-teacher/<uuid:school_id>/<str:teacher_id>/<str:request_action>/' ,TeacherAdministrationView.as_view(), name='manage-teacher'),#tasted
    
    path('teacher-record/<str:teacher_id>/',  DirectorTeacherRecordView.as_view(), name='teacher-record-add'),
    path('teacher-record/<str:teacher_id>/<str:report_action>/', DirectorTeacherRecordView.as_view(), name='teacher-record-update'),
    
]