from django.urls import path
from .consumers import FentchConsumer

websocket_urlpatterns = [
    path('ws/fentlive-server/', FentchConsumer.as_asgi()),
]
