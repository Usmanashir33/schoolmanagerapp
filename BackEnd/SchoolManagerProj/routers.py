from django.urls import path
from .consumers import SchoolConsumer,AppConsumer
from attendanceanddevices.consumers import FaceDetectionConsumer,DeviceConsumer

websocket_urlpatterns = [
    path('live-server/', AppConsumer.as_asgi()),
    path('live-server/<str:schoolId>/', SchoolConsumer.as_asgi()),
    
    path('face_detection/', FaceDetectionConsumer.as_asgi()), #Tested and working fine
    path('device_socket/<str:schoolId>/<str:deviceId>/', DeviceConsumer.as_asgi()),
]
