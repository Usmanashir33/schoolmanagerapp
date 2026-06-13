from django.urls import path
from .views import *

urlpatterns = [
    #--------------------------------ACADEMICS----------------------------
    path('create/<str:academic_item>/', AcademicView.as_view(), name='academics'), #tasted
    path('update/<str:academic_item>/<str:item_id>/', AcademicView.as_view(), name='academics-update'),#tasted
    path('delete/<uuid:school_id>/<str:academic_item>/<str:item_id>/<str:pin>/', AcademicView.as_view(), name='academics-delete'),#tasted
    path('academic-settings/<uuid:school_id>/', AcademicSettingsView.as_view(), name='school-academic-sessings'), #Tested
    
    path('details/<uuid:school_id>/<str:academic_item>/<str:item_id>/', AcademicDetailsView.as_view(), name='academics-details'),#class done,
    
    path('class/enrollment/', ClassEnrollmentView.as_view(), name='class-enrollment') , # done
    path('class/transfer/', ClassTransferView.as_view(), name='class-transfer') , # done
    path('class/subject-assignment/', ClassSubjectManagerView.as_view(), name='class-subject-assignment') , # done
    path('class/subject-substitution/', ClassSubjectManagerView.as_view(), name='class-subject-substitution') , #Done
    path('class/subject-deletion/<uuid:school_id>/<str:class_id>/<str:subject_id>/<str:pin>/', ClassSubjectManagerView.as_view(), name='class-subject-deletion') ,#Done
    
    path('class/promotion/', DirectorClassPromotionView.as_view(), name='class-promotion') ,
]