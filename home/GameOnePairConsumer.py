from channels.generic.websocket import AsyncWebsocketConsumer
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_stop
from home.ThreadVarManagerSingleton import task_manager
import json
import asyncio
import time

class GameOnePairConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle WebSocket connection."""
        print("Attempting to accept WebSocket connection...")
        await self.accept()
        print("WebSocket connection accepted")  # Debugging output

        # Initialize Redis values for shared progress and stop event
        self._initialize_redis()
        
        # Start sending updates until task_manager.stop_event is triggered
        await self._send_updates()
        print("WebSocket connection accepted")  # Debugging output

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        print("WebSocket connection closed")
        task_manager.stop_event.set()
        redis_buffer_instance.redis_1.set('wait_buffer', '1')
        await self.close()

    async def receive(self, text_data):
        """Handle messages received from WebSocket (currently not used)."""
        pass
    
    def _initialize_redis(self):
        """Initialize Redis values for shared progress and stop event."""
        redis_buffer_instance.redis_1.set('shared_progress', '0')
        redis_buffer_instance_stop.redis_1.set('stop_event_var', '0')
        redis_buffer_instance.redis_1.set('prog_when_fast', '-1')  # Reset the fast flag
        redis_buffer_instance.redis_1.set('cards_0', 'None')
        redis_buffer_instance.redis_1.set('wait_buffer', '0')

        task_manager.stop_event.clear()
    
    async def _send_updates(self):
        player_number = 0
        
        """Continuously send updates on progress and data script until stop_event_var is set."""
        with task_manager.cache_lock_event_var:
            if (int(redis_buffer_instance.redis_1.get('min').decode('utf-8')) != -1) and int(redis_buffer_instance.redis_1.get('min').decode('utf-8')) != -1:
                from_min = int(redis_buffer_instance.redis_1.get('min').decode('utf-8'))
                from_max = int(redis_buffer_instance.redis_1.get('max').decode('utf-8'))
            else:
                from_min = None
                from_max = None
        
        while True:
            if from_min is not None and from_max is not None:
                await self._send_progress_update(from_min, from_max)

            if self._should_stop():
                break

            await asyncio.sleep(0.3)  # Adjust interval as needed
        
        
        while True:
            key = 'cards'
            
            redis_buffer_instance.redis_1.set('player_number', player_number)
            print(redis_buffer_instance.redis_1.get(f'{key}_{player_number}').decode('utf-8'))

            if redis_buffer_instance.redis_1.get(f'{key}_{player_number}').decode('utf-8') != 'None':
                cards_list = json.loads(redis_buffer_instance.redis_1.get(f'{key}_{player_number}'))
                player_number += 1
                redis_buffer_instance.redis_1.set('player_number', player_number)
                if cards_list is not None:
                    await self.send(text_data=json.dumps({'cards': cards_list}))

            if redis_buffer_instance.redis_1.get('player_number').decode('utf-8') == '2':
                while redis_buffer_instance.redis_1.get('wait_buffer').decode('utf-8') == '0':
                    await asyncio.sleep(0.3)
                break  
            
            await asyncio.sleep(0.3)
        print("EXITED")
    
    async def _send_progress_update(self, from_min, from_max):
        """Retrieve and send mapped progress value."""
        # Only lock the part where progress is fetched
        with task_manager.cache_lock_progress:
            progress = int(redis_buffer_instance.redis_1.get('shared_progress').decode('utf-8'))
        mapped_progress = self._map_progress(progress, from_min, from_max)

        if mapped_progress is not None:
            if mapped_progress >= 100:
                mapped_progress = 100
            if mapped_progress != 0:
                await self.send(text_data=json.dumps({'progress': str(mapped_progress)}))
                       
    def _map_progress(self, progress, from_min, from_max):
        """Map and return the progress value to a 0-100 range."""
        if progress != 0:
            progress_when_fast = int(redis_buffer_instance.redis_1.get('prog_when_fast').decode('utf-8'))
            if progress_when_fast == 100:
                progress = from_max  # Once the condition is met, set to maximum
                redis_buffer_instance.redis_1.set('prog_when_fast', '-1')  # Reset the fast flag
            return int(self._scale_value(progress, from_min, from_max, 0, 100))
        return 0
    
    def _scale_value(self, value, from_min, from_max, to_min, to_max):
        """Scale a value from one range to another."""
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min
    
    def _should_stop(self):
        """Check if stop event or completion conditions are met."""
        # Only lock around the Redis get operation
        with task_manager.cache_lock_event_var:
            stop_event_var = redis_buffer_instance_stop.redis_1.get('stop_event_var').decode('utf-8')
        
        if stop_event_var == '1':
            task_manager.stop_event.set()

        return stop_event_var == '1'