from django.urls import path
from .views import *

urlpatterns = [
    #--------------------------------ACADEMICS----------------------------
    path('create/<str:academic_item>/', AcademicView.as_view(), name='academics'), #tasted
    path('update/<str:academic_item>/<str:item_id>/', AcademicView.as_view(), name='academics-update'),#tasted
    path('delete/<uuid:school_id>/<str:academic_item>/<str:item_id>/<str:pin>/', AcademicView.as_view(), name='academics-delete'),#tasted
    path('details/<uuid:school_id>/<str:academic_item>/<str:item_id>/', AcademicDetailsView.as_view(), name='academics-details'),#class done,
    
    path('class/enrollment/', ClassEnrollmentView.as_view(), name='class-enrollment') , # done
    path('class/transfer/', ClassTransferView.as_view(), name='class-transfer') , # done
    path('class/subject-manager/', ClassSubjectManagerView.as_view(), name='class-transfer') ,
    path('class/promotion/', DirectorClassPromotionView.as_view(), name='class-promotion') ,
]