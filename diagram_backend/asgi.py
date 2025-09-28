
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diagram_backend.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from apps.diagrams import consumers

# Aplicación HTTP estándar
http_application = get_asgi_application()

# Configuración de rutas de WebSocket
websocket_urlpatterns = [
    path("ws/collaboration/<str:diagram_id>/", consumers.CollaborationConsumer.as_asgi()),
]

# Configuración de la aplicación ASGI
application = ProtocolTypeRouter({
    "http": http_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
