from django.urls import path
from .consumers import WebSocketConsumer

websocket_urlpatterns = [
    path('ws/some_path/', WebSocketConsumer.as_asgi()),
]
