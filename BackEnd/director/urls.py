from django.urls import path
from .views import *

urlpatterns = [
    # Define your URL patterns here
    
    #------------------school--------------------------
    path('create-school/', SchoolCreateView.as_view(), name='create-school'),
    path('manage-school/', SchoolDetailView.as_view(), name='manage-school'),
   ]