from django.urls import path

from . schools_views import *

urlpatterns = [
    # Define your URL patterns here
    path('create-school/', SchoolCreateView.as_view(), name='school-create'),
]