import json
import asyncio
import time
from channels.generic.websocket import AsyncWebsocketConsumer
import traceback
from typing import Any, Dict

# Consumidor WebSocket para colaboración en diagramas
class CollaborationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Acepta la conexión y se une al grupo de colaboración.

        El error 4400 que se veía en el cliente ocurría porque:
          1. Se intentaba acceder a self.scope['loop'] (clave no existente) -> KeyError
          2. El heartbeat hacía flood (sin await real) cuando channel_layer era None
        Ambos provocaban cierre inmediato.
        """
        try:
            self.diagram_id = self.scope['url_route']['kwargs'].get('diagram_id')
            self.room_group_name = f'collaboration_{self.diagram_id}'
            print(f" conexión intentando diagrama={self.diagram_id} canal={self.channel_name}")

            if not self.channel_layer:
                print(" capa de canales no disponible, modo local (sin multiproceso)")
            else:
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()
            print(f" conectado diagrama={self.diagram_id} canal={self.channel_name}")

            # Inicializar control de logging para rate-limit
            self._last_log_ts = 0.0
            self._log_counter = 0

            # Anunciar que un usuario se unió
            await self._broadcast_internal('user_joined', {"userId": self.channel_name})

            # Iniciar heartbeat usando asyncio (intervalo estable)
            self.heartbeat_task = asyncio.create_task(self._heartbeat())
        except Exception as e:
            print(f" fallo en conexión: {e}\n{traceback.format_exc()}")
            await self.close(code=4400)

    async def disconnect(self, close_code):
        try:
            print(f" desconectar diagrama={getattr(self,'diagram_id',None)} canal={self.channel_name} código={close_code}")
            if hasattr(self, 'heartbeat_task'):
                self.heartbeat_task.cancel()
            # Avisar salida sólo si hubo connect exitoso
            if getattr(self, 'diagram_id', None):
                await self._broadcast_internal('user_left', {"userId": self.channel_name})
            if hasattr(self, 'room_group_name') and self.channel_layer:
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception as e:
            print(f" error en desconexión: {e}")

    async def receive(self, text_data):
        """Procesa mensajes entrantes del cliente y los redistribuye.

        Protocolo esperado por el frontend (ver use-colaborativo.ts):
        - user_joined
        - user_left
        - cursor_move
        - class_update -> broadcast como class_updated
        - relationship_update -> broadcast como relationship_updated
        - request_initial_state -> se reenvía a todos con userId
        - initial_state (solo a un destinatario)
        """
        try:
            data = json.loads(text_data)
        except Exception as e:
            print(f" JSON inválido: {e} dato={text_data[:150]}")
            return

        event_type = data.get('type')
        # Aceptar tanto 'payload' como 'data' (flexibilidad con el frontend)
        payload = data.get('payload') or data.get('data') or {}
        # Rate limiting del log para eventos muy frecuentes (ej. drag produce muchos class_update)
        if event_type == 'class_update':
            now = time.time()
            self._log_counter += 1
            # Log solo si pasaron >=0.3s desde el último log o cada 25º mensaje
            if (now - getattr(self, '_last_log_ts', 0)) >= 0.3 or (self._log_counter % 25) == 0:
                print(f" evento class_update diagrama={getattr(self,'diagram_id',None)} total={self._log_counter}")
                self._last_log_ts = now
        else:
            if event_type not in ('cursor_move', 'ping'):
                print(f" evento {event_type} diagrama={getattr(self,'diagram_id',None)}")

        # Adjuntar emisor
        if isinstance(payload, dict):
            payload.setdefault('userId', self.channel_name)

        # Optimizaciones de diffs: para class_update / relationship_update si incluyen 'previous'
        # calculamos únicamente los campos nuevos/cambiados y enviamos 'delta'.
        # El frontend puede aplicar delta si existe, o usar payload completo si no.
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
            # Limpiar claves grandes opcionales que ya no necesitemos (para reducir broadcast)
            # Mantener 'current' si el frontend lo usa como fuente de verdad; si no, se podría quitar.

        # Handshake: request estado inicial
        if event_type == 'request_initial_state':
            payload['userId'] = payload.get('userId') or self.channel_name

        # initial_state: devolver solo al solicitante
        if event_type == 'initial_state':
            to_user = payload.get('toUserId')
            if to_user == self.channel_name:
                # ignorar si me estoy enviando a mí mismo
                return
            # En este diseño simple se hace broadcast y el receptor filtra; para optimizar necesitaríamos channel_name directo.
            # Continuamos para broadcast (frontend filtra por toUserId)

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
        except Exception as e:
            print(f" fallo al enviar: {e}")
    async def _heartbeat(self):
        """Envía un ping cada 25s.

        Antes se generaba flood porque no había un await real cuando no existía channel_layer.
        """
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
