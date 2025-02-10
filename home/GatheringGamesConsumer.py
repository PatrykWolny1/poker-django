from channels.generic.websocket import AsyncWebsocketConsumer
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_stop
from home.ThreadVarManagerSingleton import task_manager
import json
import asyncio
import time
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async, async_to_sync

class GatheringGamesConsumer(AsyncWebsocketConsumer):
    iteration = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.name = "gathering_games"
        self.stop_event_var = False

    async def connect(self):
        GatheringGamesConsumer.iteration += 1

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
        if GatheringGamesConsumer.iteration == 1:
            await self._send_updates()
            await self._send_updates_gathering()
        else:
            await self._send_updates_gathering()

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
        """Handle messages received from WebSocket."""
        print("Receive method triggered")
        
        # try:
        data = json.loads(text_data)
        action = data.get('action')
        reason = data.get('reason')
        session_id = data.get('session_id')

        if action == 'close':
            if reason == 'on_refresh':
                GatheringGamesConsumer.iteration = 0
                print(GatheringGamesConsumer.iteration)

    async def _send_updates(self):        
        """Continuously send updates on progress and data script until stop_event_var is set."""
        if (int(redis_buffer_instance.redis_1.get(f'min_{self.session_id}').decode('utf-8')) != -1) and int(redis_buffer_instance.redis_1.get(f'max_{self.session_id}').decode('utf-8')) != -1:
            from_min = int(redis_buffer_instance.redis_1.get(f'min_{self.session_id}').decode('utf-8'))
            from_max = int(redis_buffer_instance.redis_1.get(f'max_{self.session_id}').decode('utf-8'))
        else:
            from_min = None
            from_max = None

        while True:
            if from_min is not None and from_max is not None:
                await self._send_progress_update(from_min, from_max)

            print("In _send_updates...")

            if self._should_stop():
                await asyncio.sleep(0.2)
                break

            await asyncio.sleep(0.1)  # Adjust interval as needed
       
    async def _send_updates_gathering(self):     
        task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"].clear()   
        redis_buffer_instance.redis_1.set(f'shared_progress_gathering_{self.session_id}', '-1')
        self.stop_event_var = False

        while True:
            progress = int(float(redis_buffer_instance.redis_1.get(f'shared_progress_gathering_{self.session_id}').decode('utf-8')))
            
            if progress is not None:
                if progress >= 100:
                    progress = 100
                if progress >= 0:
                    progress_data = {f'progress_gathering_games_{self.session_id}': str(progress)}
                    print(f"Progress data to send: {progress_data}")
                    progress_to_send = f'progress_gathering_games_{self.session_id}'
                    await self.send(text_data=json.dumps({str(progress_to_send) : str(progress)}))
            
            print("In _send_updates_gathering...")

            if self._should_stop():
                await asyncio.sleep(0.2)
                break

            await asyncio.sleep(0.2)  # Adjust interval as needed

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