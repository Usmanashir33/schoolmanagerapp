from django.urls import path
from .consumers import FentchConsumer

websocket_urlpatterns = [
    path('ws/backendlive-server/', FentchConsumer.as_asgi()),
]
