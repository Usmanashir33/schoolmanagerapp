from django.urls import path

from . views import  *

urlpatterns = [
    # Define your URL patterns here
    
    # path('manage-student/', StudentCreateView.as_view(), name='manage-student'),
    path('register-new-school/', SchoolAndDirectorCreateView.as_view(), name='create-school'), #tested
]  