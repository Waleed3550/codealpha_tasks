import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)

class TaskBoardConsumer(AsyncWebsocketConsumer):
    """
    Handles realtime bi-directional communication for Kanban boards and live cursors.
    """
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_group_name = f'project_{self.project_id}'

        # Join project room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected to {self.room_group_name}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected from {self.room_group_name}")

    # Receive message from WebSocket (Client -> Server)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        data = text_data_json.get('data')

        # Broadcast the message to the entire project room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'board_update',
                'action': action,
                'data': data
            }
        )

    # Receive message from room group and push to individual client
    async def board_update(self, event):
        action = event['action']
        data = event['data']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': action,
            'data': data
        }))
