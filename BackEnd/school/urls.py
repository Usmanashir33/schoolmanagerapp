from django.urls import path

from . schools_views import *
from . teacher_views import *
from . section_views import *
from . student_views import *
from . classroom_views import *

urlpatterns = [
    # Define your URL patterns here
    
    #------------------school--------------------------
    path('create-school/', SchoolCreateView.as_view(), name='create-school'),
    path('manage-school/', DirectorSchoolDetailView.as_view(), name='manage-school'),
    
    #-----------------Student-------------------------
    path('manage-student/', SchoolCreateView.as_view(), name='manage-student'),
    # path('delete-student/', SchoolCreateView.as_view(), name='school-create'),
    
    #-----------------classroom--------------------------------
    path('manage-classroom/', DirectorClassRoomView.as_view(), name='manage-classroom'),
    path('delete-classroom/', DirectorDeleteClassRoomView.as_view(), name='delete-classroom'),
    
    #-----------------Section------------------------------
    path('manage-section/', DirectorSectionDeleteView.as_view(), name='manage-section'),
    path('delete-section/', DirectorSectionView.as_view(), name='delete-section'),
]