import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from home.redis_buffer_singleton import redis_buffer_instance
import config
from home.views import stop_event

class TestConsumer(AsyncWebsocketConsumer):
    def map_value(self, value, from_min=1, from_max=42, to_min=1, to_max=100):
        # Map value from the original range to the new range
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min
    
    async def connect(self):        
        await self.accept()  # Accept the WebSocket connection
        print("WebSocket connection accepted") # Debugging output

        stop_loop = cache.get('stop_loop')
        
        # Keep sending progress updates
        # Continuously check for progress updates in cache   
        while not stop_event.is_set():
            stop_loop = cache.get('stop_loop')
            progress = cache.get('shared_variable', None)  # Retrieve from cache
            progress = int(progress)
            
            progress = int(self.map_value(progress, 1, 21, 1, 100))

            data_script = redis_buffer_instance.read_from_buffer('prog')    

            if progress is not None:
                print("IN CONSUM: ", stop_event)
                print(f"WebSocket Consumer: Progress Retrieved - {str(progress)}%")  # Debugging output
                
                await self.send(text_data=json.dumps({'progress': str(progress)}))

            if data_script is not None:
                data_script = data_script.decode('utf-8').strip()
                await self.send(text_data=json.dumps({'data_script': str(data_script)}))
            
            if progress == 100:
                break
            
            await asyncio.sleep(0.5)  # Adjust the interval as needed
            
    async def disconnect(self, close_code):
        print("WebSocket connection closed")

    async def receive(self, text_data):
        # Handle messages received from the WebSocket if needed
        pass

