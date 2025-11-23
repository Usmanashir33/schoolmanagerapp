from django.urls import path
from .consumers import FentchConsumer

websocket_urlpatterns = [
    path('ws/so/', FentchConsumer.as_asgi()),
]
