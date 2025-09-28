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
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            print(f"[WS] connected diagram_id={self.diagram_id} channel={self.channel_name}")
        except Exception as e:
            print(f"[WS][ERROR] connect failed: {e}\n{traceback.format_exc()}")
            # Rechazar conexión si algo falla
            await self.close(code=4400)

    async def disconnect(self, close_code):
        try:
            print(f"[WS] disconnect diagram_id={getattr(self,'diagram_id',None)} channel={self.channel_name} code={close_code}")
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception as e:
            print(f"[WS][ERROR] during disconnect: {e}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except Exception as e:
            print(f"[WS][ERROR] invalid JSON: {e} raw={text_data[:200]}")
            return
        event_type = data.get('type')
        payload = data.get('payload', {})
        print(f"[WS] recv type={event_type} diagram={getattr(self,'diagram_id',None)}")
        target = {
            'type': 'collaboration_event',
            'event_type': event_type,
            'payload': payload,
        }
        await self.channel_layer.group_send(self.room_group_name, target)

    async def collaboration_event(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': event['event_type'],
                'payload': event['payload'],
            }))
            if event['event_type'] and event['event_type'].endswith('_update'):
                await self.send(text_data=json.dumps({
                    'type': event['event_type'] + 'd',
                    'payload': event['payload'],
                }))
        except Exception as e:
            print(f"[WS][ERROR] send failure: {e}")
