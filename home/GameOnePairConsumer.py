from channels.generic.websocket import AsyncWebsocketConsumer
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_stop
from home.ThreadVarManagerSingleton import task_manager
import json
import asyncio

class GameOnePairConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        await self.accept()
        print("WebSocket connection accepted")  # Debugging output

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        print("WebSocket connection closed")

    async def receive(self, text_data):
        """Handle messages received from WebSocket (currently not used)."""
        pass