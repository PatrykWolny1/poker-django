from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_stop
from home.views import data_ready_event, stop_event, cache_lock_progress, cache_lock_event_var
import json
import asyncio
import time 

class TestConsumer(AsyncWebsocketConsumer):
    def map_value(self, value, from_min, from_max, to_min=0, to_max=100):
        # Map value from the original range to the new range
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min
    
    async def connect(self):        
        await self.accept()  # Accept the WebSocket connection
        
        print("WebSocket connection accepted") # Debugging output

        cache.set('shared_progress', '0')
        progress = int(cache.get('shared_progress'))
        
        redis_buffer_instance_stop.redis_1.set('stop_event_var', '0')
        stop_event_var = redis_buffer_instance_stop.redis_1.get('stop_event_var').decode('utf-8')

        # Keep sending progress updates
        # Continuously check for progress updates in cache   
        while not stop_event.is_set():
            from_min = int(redis_buffer_instance.redis_1.get('min').decode('utf-8'))
            from_max = int(redis_buffer_instance.redis_1.get('max').decode('utf-8'))
        
            stop_event_var = redis_buffer_instance_stop.redis_1.get('stop_event_var').decode('utf-8') 
            if stop_event_var != '0':
                break
            
            # Clear the update event so the producer can set it again
            data_ready_event.clear()

            with cache_lock_progress:
                progress = int(cache.get('shared_progress', '0'))  # Retrieve from cache
                processed_progress = self.send_map_progress(progress, from_min, from_max)
                if processed_progress is not None:
                    if processed_progress > 100:
                        processed_progress = 100
                    print(processed_progress)
                    print(from_min, from_max)
                    await self.send(text_data=json.dumps({'progress': str(processed_progress)}))

            with cache_lock_event_var:
                data_script = redis_buffer_instance.read_from_buffer('prog')   
                processed_data_script = self.send_data_print(data_script)
                if processed_data_script is not None:
                    await self.send(text_data=json.dumps({'data_script': str(processed_data_script)}))  

            if (processed_progress == 100) or stop_event.is_set():
                with cache_lock_event_var:
                    cache.set('shared_progress', '100') 
                break

            await asyncio.sleep(0.2)  # Adjust the interval as needed

    async def disconnect(self, close_code):
        print("WebSocket connection closed")

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("action") == "request_latest_data_script":
            with cache_lock_event_var:
                data_script = redis_buffer_instance.read_from_buffer('prog')
                processed_data_script = self.send_data_print(data_script)
                if processed_data_script is not None:
                    await self.send(text_data=json.dumps({'data_script': str(processed_data_script)}))
                    
    def send_data_print(self, data_script):
        data_ready_event.clear()  
        
        if data_script is not None: 
            data_script = data_script.decode('utf-8').strip("\n")
        
        return data_script
        
    def send_map_progress(self, progress_in, from_min, from_max):
        progress = int(progress_in)    
        
        progress_when_fast = int(redis_buffer_instance.redis_1.get('prog_when_fast').decode('utf-8'))
        # print(progress_when_fast)
        
            
        # print(from_min, from_max)
        data_ready_event.clear()
        
        if progress != 0:
            if progress_when_fast == 100:
                progress = from_max

            progress = int(self.map_value(progress, from_min, from_max, 0, 100))
            # print(f"WebSocket Consumer: Progress Retrieved - {str(progress)}%")  # Debugging output
            return int(progress)
        return 0

