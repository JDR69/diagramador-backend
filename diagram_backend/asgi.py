
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from apps.diagrams import WebSocket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diagram_backend.settings')

django_app = get_asgi_application()

# Unificamos HTTP (Django) + WebSockets (Channels)
application = ProtocolTypeRouter({
	'http': django_app,
	'websocket': AuthMiddlewareStack(
		URLRouter([
			path('ws/collaboration/<str:diagram_id>/', WebSocket.CollaborationConsumer.as_asgi()),
		])
	)
})
