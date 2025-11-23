from django.urls import path
from .consumers import FentchConsumer

websocket_urlpatterns = [
    path('ws/some_pa/', FentchConsumer.as_asgi()),
]
