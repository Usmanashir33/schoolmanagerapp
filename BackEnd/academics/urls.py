from django.urls import path
from .views import *

urlpatterns = [
    #--------------------------------ACADEMICS----------------------------
    path('create/<str:academic_item>/',               AcademicView.as_view(), name='academics'), #tasted
    path('update/<str:academic_item>/<str:item_id>/', AcademicView.as_view(), name='academics-update'),#tasted
    path('delete/<uuid:school_id>/<str:academic_item>/<str:item_id>/<str:pin>/', AcademicView.as_view(), name='academics-delete'),#tasted
    
    path('class/transfer/', DirectorClassTransferView.as_view(), name='class-transfer') ,
    path('class/promotion/', DirectorClassPromotionView.as_view(), name='class-promotion') ,
]