import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles realtime bi-directional communication for Chat Rooms.
    """
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser())
        if self.user.is_anonymous:
            logger.warning("Unauthenticated websocket connection attempt.")
            await self.close()
            return

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected to {self.room_group_name} by {self.user.email}")

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"WebSocket disconnected from {self.room_group_name}")

    @database_sync_to_async
    def save_message(self, room_id, user, content):
        from .models import Message, ChatRoom
        try:
            room = ChatRoom.objects.get(id=room_id)
            return Message.objects.create(room=room, sender=user, content=content)
        except ChatRoom.DoesNotExist:
            return None

    # Receive message from WebSocket (Client -> Server)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        data = text_data_json.get('data')

        if action == 'send_message':
            content = data.get('content')
            if content:
                msg = await self.save_message(self.room_id, self.user, content)
                if msg:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'action': 'new_message',
                            'data': {
                                'id': str(msg.id),
                                'content': msg.content,
                                'sender': self.user.email,
                                'sender_id': str(self.user.id),
                                'created_at': msg.created_at.isoformat()
                            }
                        }
                    )
        elif action == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'action': 'typing',
                    'data': {
                        'user': self.user.email,
                        'user_id': str(self.user.id),
                        'is_typing': data.get('is_typing', True)
                    }
                }
            )

    # Receive message from room group and push to individual client
    async def chat_message(self, event):
        action = event['action']
        data = event['data']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': action,
            'data': data
        }))
