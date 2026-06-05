from django.urls import path

# from .academic_views import *
from academics.views import *
from .school_views import *
from .director_views import *

urlpatterns = [
    # Define your URL patterns here
    #------------------Director--------------------------
    path('update/', DirectorDetailView.as_view(), name='update-detail'), #Tested
    path('security-settings/<uuid:school_id>/', DirectorSettingsView.as_view(), name='security-settings'), #Tested
    
    #------------------school--------------------------
    # GET tested ,PUT tested , POST for DELETE is Tested
    path('academic-settings/<uuid:school_id>/', DirectorAcademicSettingsView.as_view(), name='school-detail'), #Tested

   ]