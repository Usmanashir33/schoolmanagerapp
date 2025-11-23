from django.urls import path
from .consumers import FentchConsumer

websocket_urlpatterns = [
    path('backend-live-server/', FentchConsumer.as_asgi()),
]
