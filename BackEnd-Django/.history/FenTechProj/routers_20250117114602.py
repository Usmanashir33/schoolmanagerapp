from django.urls import path
from .consumers import FentchConsumer

websocket_urlpatterns = [
    path('ws/backend-live-server/', FentchConsumer.as_asgi()),
]
