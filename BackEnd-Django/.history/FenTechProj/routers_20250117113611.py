from django.urls import path
from your_app_name.consumers import MyWebSocketConsumer

websocket_urlpatterns = [
    path('ws/some_path/', MyWebSocketConsumer.as_asgi()),
]
