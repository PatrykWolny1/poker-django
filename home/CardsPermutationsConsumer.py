from channels.generic.websocket import AsyncWebsocketConsumer
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_stop
from home.ThreadVarManagerSingleton import task_manager
import json
import asyncio
import time
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async, async_to_sync

class CardsPermutationsConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.name = "thread_perms_combs"
        self.stop_event_var = False

    async def connect(self):
        """Handle WebSocket connection."""
        # Generate a session if it doesn't exist
        session = self.scope["session"]

        if not self.session_id:
            await sync_to_async(session.save)()  # Ensure this operation is run in a thread-safe manner
            self.session_id = self.scope["session"].session_key
        
        self.session_id = redis_buffer_instance.redis_1.get(self.session_id).decode('utf-8')
        
        self.group_name = f"group_{self.session_id}"

        await self.channel_layer.group_add (
            self.group_name,
            self.channel_name
        )

        task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"].clear() 
        task_manager.session_threads[self.session_id][self.name].event["stop_event_immediately"].clear() 

        if not self.session_id:
            print("No session ID provided. Closing WebSocket.")
            await self.close()
            return

        if self.session_id not in task_manager.session_threads:
            print(f"Session thread for {self.session_id} not initialized. Closing connection.")
            await self.close(code=4001)
            return
        
        print("Attempting to accept WebSocket connection...", flush=True)
        await self.accept()
        print(f"WebSocket connected with session ID: {self.session_id}", flush=True)

        redis_buffer_instance.redis_1.set(f'connection_accepted_{self.session_id}', 'yes')
        
        # Start sending updates until task_manager.stop_event is triggered
        await self._send_updates()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        task_manager.session_threads[self.session_id][self.name].thread[self.session_id].join()
        
        del task_manager.session_threads[self.session_id]

        await self.channel_layer.group_discard (
            self.group_name,
            self.channel_name
        )
        
        print(f"WebSocket connection closed for session {self.session_id}", flush=True)

    async def receive(self, text_data):
        """Handle messages received from WebSocket (currently not used)."""
        pass
        
    async def _send_updates(self):        
        """Continuously send updates on progress and data script until stop_event_var is set."""
        if (int(redis_buffer_instance.redis_1.get(f'min_{self.session_id}').decode('utf-8')) != -1) and int(redis_buffer_instance.redis_1.get(f'max_{self.session_id}').decode('utf-8')) != -1:
            from_min = int(redis_buffer_instance.redis_1.get(f'min_{self.session_id}').decode('utf-8'))
            from_max = int(redis_buffer_instance.redis_1.get(f'max_{self.session_id}').decode('utf-8'))
        else:
            from_min = None
            from_max = None

        while True:
            await self._send_data_script(f'print_gen_combs_perms_{self.session_id}')
            if from_min is not None and from_max is not None:
                await self._send_progress_update(from_min, from_max)

            if self._should_stop():
                await self._finalize_progress()
                await self.close(code=4001)
                return
            
            print("In _send_updates...")
            
            await asyncio.sleep(0.6)  # Adjust interval as needed

    async def _send_progress_update(self, from_min, from_max):
        """Retrieve and send mapped progress value."""
        # Only lock the part where progress is fetched
        progress = int(redis_buffer_instance.redis_1.get(f'shared_progress_{self.session_id}').decode('utf-8'))

        mapped_progress = self._map_progress(progress, from_min, from_max)
        print("Progress: ", mapped_progress)
        if mapped_progress is not None:
            if mapped_progress >= 100:
                mapped_progress = 100
            if mapped_progress != 0:
                progress_data = {f'progress_{self.session_id}': str(mapped_progress)}
                print(f"Progress data to send: {progress_data}")
                progress_to_send = f'progress_{self.session_id}'
                await self.send(text_data=json.dumps({str(progress_to_send) : str(mapped_progress)}))

    async def _send_data_script(self, key):
        """Retrieve and send the data script if updated."""
        data_script = redis_buffer_instance.redis_1.get(key)
        redis_buffer_instance.redis_1.set(key, '-1')
                        
        processed_data_script = self._process_data_script(data_script)
        if processed_data_script != '-1':
            await self.send(text_data=json.dumps({f'data_script_{self.session_id}': processed_data_script}))

    def _map_progress(self, progress, from_min, from_max):
        """Map and return the progress value to a 0-100 range.""" 
        if progress != 0:
            progress_when_fast = int(redis_buffer_instance.redis_1.get(f'prog_when_fast_{self.session_id}').decode('utf-8'))
            if progress_when_fast == 100:
                progress = from_max  # Once the condition is met, set to maximum
                redis_buffer_instance.redis_1.set('prog_when_fast', '-1')  # Reset the fast flag
            return int(self._scale_value(progress, from_min, from_max, 0, 100))
        return 0

    def _scale_value(self, value, from_min, from_max, to_min, to_max):
        """Scale a value from one range to another."""
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

    def _process_data_script(self, data_script):
        """Process and return the data script if valid."""
        if data_script:
            return data_script.decode('utf-8').strip("\n")
        return None

    def _should_stop(self):
        """Check if stop event or completion conditions are met."""
        if task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"].is_set():
            print(task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"])
            self.stop_event_var = True

        return self.stop_event_var

    async def _finalize_progress(self):
        """Finalize the progress to 100% and send final updates."""
        # Only lock around the Redis set and get operations
        final_data_script = None
        
        if redis_buffer_instance_stop.redis_1.get(f'count_arrangements_stop_{self.session_id}').decode('utf-8') != '-1':
            final_data_script = redis_buffer_instance_stop.redis_1.get(f'count_arrangements_stop_{self.session_id}')
            redis_buffer_instance_stop.redis_1.set(f'count_arrangements_stop_{self.session_id}', '-1')
        if redis_buffer_instance_stop.redis_1.get(f'count_arrangements_{self.session_id}').decode('utf-8') != '-1':
            final_data_script = redis_buffer_instance.redis_1.get(f'count_arrangements_{self.session_id}')
            redis_buffer_instance.redis_1.set(f'count_arrangements_{self.session_id}', '-1')
        
        redis_buffer_instance.redis_1.set(f'shared_progress_{self.session_id}', '100')
    
        processed_data_script = self._process_data_script(final_data_script)
        if processed_data_script is not None:
            await self.send(text_data=json.dumps({f'data_script_{self.session_id}': processed_data_script}))