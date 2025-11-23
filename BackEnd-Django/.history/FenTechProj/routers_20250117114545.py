from django.urls import path
from .consumers import FentchConsumer

websocket_urlpatterns = [
    path('ws/li/', FentchConsumer.as_asgi()),
]
