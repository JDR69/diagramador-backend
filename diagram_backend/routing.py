
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from backend.apps.diagrams import WebSocket

application = ProtocolTypeRouter({
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/collaboration/<str:diagram_id>/", WebSocket.CollaborationConsumer.as_asgi()),
        ])
    ),
})
