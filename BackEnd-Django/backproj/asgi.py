"""
ASGI config for fentechbackproj fentechbackproject.
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# Set default settings module before anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fentechbackproj.settings')

# 👇 Initialize Django before importing anything that touches models
django_asgi_app = get_asgi_application()

# 👇 Now it's safe to import websocket routes
from .routers import websocket_urlpatterns

# ASGI application setup
application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
