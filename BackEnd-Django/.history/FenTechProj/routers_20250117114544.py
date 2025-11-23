from django.urls import path
from .consumers import FentchConsumer

websocket_urlpatterns = [
    path('ws//', FentchConsumer.as_asgi()),
]
