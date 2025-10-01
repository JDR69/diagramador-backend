import json
import asyncio
import time
from channels.generic.websocket import AsyncWebsocketConsumer
import traceback
from typing import Any, Dict

# Consumidor WebSocket para colaboración en diagramas
class CollaborationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Acepta la conexión y se une al grupo de colaboración."""
        try:
            self.diagram_id = self.scope['url_route']['kwargs'].get('diagram_id')
            self.room_group_name = f'collaboration_{self.diagram_id}'

            if not self.channel_layer:
                pass  # modo local sin multiproceso
            else:
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()

            # Inicializar control de logging para rate-limit
            self._last_log_ts = 0.0
            self._log_counter = 0

            # Anunciar que un usuario se unió
            await self._broadcast_internal('user_joined', {"userId": self.channel_name})

            # Iniciar heartbeat usando asyncio
            self.heartbeat_task = asyncio.create_task(self._heartbeat())
        except Exception as e:
            await self.close(code=4400)

    async def disconnect(self, close_code):
        try:
            if hasattr(self, 'heartbeat_task'):
                self.heartbeat_task.cancel()
            # Avisar salida sólo si hubo connect exitoso
            if getattr(self, 'diagram_id', None):
                await self._broadcast_internal('user_left', {"userId": self.channel_name})
            if hasattr(self, 'room_group_name') and self.channel_layer:
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception:
            pass

    async def receive(self, text_data):
        """Procesa mensajes entrantes del cliente y los redistribuye."""
        try:
            data = json.loads(text_data)
        except Exception:
            return

        event_type = data.get('type')
        # Aceptar tanto 'payload' como 'data' (flexibilidad con el frontend)
        payload = data.get('payload') or data.get('data') or {}
        
        # Rate limiting del log para eventos muy frecuentes
        if event_type == 'class_update':
            now = time.time()
            self._log_counter += 1
        # Sin logs para otros eventos tampoco

        # Adjuntar emisor
        if isinstance(payload, dict):
            payload.setdefault('userId', self.channel_name)

        # Optimizaciones de diffs: para class_update / relationship_update si incluyen 'previous'
        if event_type in ("class_update", "relationship_update") and isinstance(payload, dict):
            prev = payload.get('previous')
            curr = payload.get('current') or payload.get('data') or payload
            if isinstance(prev, dict) and isinstance(curr, dict):
                delta: Dict[str, Any] = {}
                for k, v in curr.items():
                    if prev.get(k) != v:
                        delta[k] = v
                # Sólo añadimos delta si hay diferencias y no es todo el objeto
                if delta and len(delta) < len(curr):
                    payload['delta'] = delta

        # Handshake: request estado inicial
        if event_type == 'request_initial_state':
            payload['userId'] = payload.get('userId') or self.channel_name

        # initial_state: devolver solo al solicitante
        if event_type == 'initial_state':
            to_user = payload.get('toUserId')
            if to_user == self.channel_name:
                return

        translate_map = {
            'class_update': 'class_updated',
            'relationship_update': 'relationship_updated',
        }
        outbound_type = translate_map.get(event_type, event_type)
        envelope = {
            'type': 'collaboration_event',
            'event_type': outbound_type,
            'payload': {**payload, 'timestamp': payload.get('timestamp') or __import__('time').time()},
        }

        if self.channel_layer:
            await self.channel_layer.group_send(self.room_group_name, envelope)
        else:  # modo local sin capa -> envío directo
            await self.collaboration_event(envelope)

    async def collaboration_event(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': event['event_type'],
                'payload': event['payload'],
            }))
        except Exception:
            pass
    
    async def _heartbeat(self):
        """Envía un ping cada 25s."""
        try:
            while True:
                await self.send(text_data=json.dumps({'type': 'ping'}))
                await asyncio.sleep(25)
        except Exception:
            pass

    async def _broadcast_internal(self, event_type: str, payload: dict):
        """Utilidad para emitir eventos internos (user_joined / user_left)."""
        envelope = {
            'type': 'collaboration_event',
            'event_type': event_type,
            'payload': {**payload, 'timestamp': __import__('time').time()},
        }
        if self.channel_layer:
            await self.channel_layer.group_send(self.room_group_name, envelope)
        else:
            await self.collaboration_event(envelope)
