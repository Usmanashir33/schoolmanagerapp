from django.urls import path
from .consumers import AppConsumer

websocket_urlpatterns = [
    path('live-server/', AppConsumer.as_asgi()),
]
