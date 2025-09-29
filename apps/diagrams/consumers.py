import json
from channels.generic.websocket import AsyncWebsocketConsumer
import traceback

# Consumidor WebSocket para colaboración en diagramas
class CollaborationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.diagram_id = self.scope['url_route']['kwargs']['diagram_id']
            self.room_group_name = f'collaboration_{self.diagram_id}'
            print(f"[WS] connect attempt diagram_id={self.diagram_id} channel={self.channel_name}")
            if not self.channel_layer:  # capa no disponible
                print("[WS][WARN] channel_layer no disponible, usando conexión directa sin grupos")
            else:
                await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            print(f"[WS] connected diagram_id={self.diagram_id} channel={self.channel_name}")
            # Iniciar heartbeat (ping) para mantener viva la conexión en Azure LB
            self.heartbeat_task = self.scope['loop'].create_task(self._heartbeat())
        except Exception as e:
            print(f"[WS][ERROR] connect failed: {e}\n{traceback.format_exc()}")
            # Rechazar conexión si algo falla
            await self.close(code=4400)

    async def disconnect(self, close_code):
        try:
            print(f"[WS] disconnect diagram_id={getattr(self,'diagram_id',None)} channel={self.channel_name} code={close_code}")
            if hasattr(self, 'heartbeat_task'):
                self.heartbeat_task.cancel()
            if hasattr(self, 'room_group_name') and self.channel_layer:
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception as e:
            print(f"[WS][ERROR] during disconnect: {e}")

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
            print(f"[WS][ERROR] invalid JSON: {e} raw={text_data[:150]}")
            return
        event_type = data.get('type')
        payload = data.get('payload', {}) or {}
        print(f"[WS] recv type={event_type} diagram={getattr(self,'diagram_id',None)}")

        # Adjuntar emisor
        if isinstance(payload, dict):
            payload.setdefault('userId', self.channel_name)

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
        else:
            await self.collaboration_event(envelope)

    async def collaboration_event(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': event['event_type'],
                'payload': event['payload'],
            }))
        except Exception as e:
            print(f"[WS][ERROR] send failure: {e}")

    async def _heartbeat(self):
        try:
            while True:
                await self.send(text_data=json.dumps({'type': 'ping'}))
                await self.channel_layer.sleep(25) if self.channel_layer else self.scope['loop'].call_later(25, lambda: None)
        except Exception:
            pass
