import json
import asyncio
import subprocess
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
import time
import asyncio


class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()  # Accept the WebSocket connection

        # Keep sending progress updates
        while True:
            # Simulate progress updates (for demonstration)
            for i in range(101):
                await self.send(text_data=json.dumps({'progress': i}))
                await asyncio.sleep(1)  # Simulate delay for updates
            
            # Break after reaching 100% progress
            break

    async def disconnect(self, close_code):
        print("WebSocket connection closed")

    async def receive(self, text_data):
        # Handle messages received from the WebSocket if needed
        pass
