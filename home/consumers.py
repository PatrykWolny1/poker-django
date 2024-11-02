from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_stop
from home.views import data_ready_event, stop_event, cache_lock_progress, cache_lock_event_var
import json
import asyncio

class TestConsumer(AsyncWebsocketConsumer):
    def map_value(self, value, from_min=1, from_max=42, to_min=1, to_max=100):
        # Map value from the original range to the new range
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min
    
    async def connect(self):        
        await self.accept()  # Accept the WebSocket connection
        
        print("WebSocket connection accepted") # Debugging output

        cache.set('shared_progress', 0)
        progress = cache.get('shared_progress')

        redis_buffer_instance_stop.redis_1.set('stop_event_var', '0')
        stop_event_var = redis_buffer_instance_stop.redis_1.get('stop_event_var')
        
        # Keep sending progress updates
        # Continuously check for progress updates in cache   
        while not stop_event.is_set() and stop_event_var == b'0':
            stop_event_var = redis_buffer_instance_stop.redis_1.get('stop_event_var') 

            # Clear the update event so the producer can set it again
            data_ready_event.clear()

            with cache_lock_progress:
                progress = cache.get('shared_progress', 0)  # Retrieve from cache
                progress = self.send_map_progress(progress)
                await self.send(text_data=json.dumps({'progress': str(progress)}))

            with cache_lock_event_var:
                data_script = redis_buffer_instance.read_from_buffer('prog')   
                data_script = self.send_data_print(data_script)
                if data_script is not None:
                    await self.send(text_data=json.dumps({'data_script': str(data_script)}))  

            if progress > 100 or stop_event.is_set():
                with cache_lock_event_var:
                    cache.set('shared_progress', 0) 
                break

            await asyncio.sleep(0.5)  # Adjust the interval as needed

    async def disconnect(self, close_code):
        print("WebSocket connection closed")

    async def receive(self, text_data):
        # Handle messages received from the WebSocket if needed
        pass
    
    def send_data_print(self, data_script):
        data_ready_event.clear()  
        
        if data_script is not None: 
            data_script = data_script.decode('utf-8').strip("\n")
        
        return data_script
        
    def send_map_progress(self, progress):
        progress = int(progress)    
        
        data_ready_event.clear()
        
        if progress != 0:
            progress = int(self.map_value(progress, 0, 21, 0, 100)) 
            
            # print(f"WebSocket Consumer: Progress Retrieved - {str(progress)}%")  # Debugging output
                        
            return int(progress)
        return 0

