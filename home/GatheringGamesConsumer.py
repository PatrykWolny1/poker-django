from channels.generic.websocket import AsyncWebsocketConsumer
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_stop
from home.ThreadVarManagerSingleton import task_manager
import json
import asyncio
import time
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async, async_to_sync

class GatheringGamesConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for gathering game data and progress updates."""
    
    iteration = 0  # Class variable to track the number of iterations

    def __init__(self, *args, **kwargs):
        """Initialize the WebSocket consumer."""
        super().__init__(*args, **kwargs)
        self.session_id = None  # Unique session ID for the WebSocket connection
        self.name = "gathering_games"  # Name identifier for this consumer
        self.stop_event_var = False  # Flag to track if the consumer should stop

    async def connect(self):
        """Handle WebSocket connection."""
        GatheringGamesConsumer.iteration += 1  # Increment iteration count
        
        session = self.scope["session"]

        # Ensure a session ID exists
        if not self.session_id:
            await sync_to_async(session.save)()  # Save session in a thread-safe way
            self.session_id = self.scope["session"].session_key

        # Retrieve session ID from Redis
        self.session_id = redis_buffer_instance.redis_1.get(self.session_id).decode('utf-8')

        # Define a unique WebSocket group for the session
        self.group_name = f"group_{self.session_id}"

        # Add WebSocket connection to the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Clear stop events before starting
        task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"].clear()
        task_manager.session_threads[self.session_id][self.name].event["stop_event_immediately"].clear()

        # Validate session ID before proceeding
        if not self.session_id:
            print("No session ID provided. Closing WebSocket.")
            await self.close()
            return

        # Ensure session thread exists in task manager
        if self.session_id not in task_manager.session_threads:
            print(f"Session thread for {self.session_id} not initialized. Closing connection.")
            await self.close(code=4001)
            return

        # Accept the WebSocket connection
        print("Attempting to accept WebSocket connection...", flush=True)
        await self.accept()
        print(f"WebSocket connected with session ID: {self.session_id}", flush=True)

        # Store connection status in Redis
        redis_buffer_instance.redis_1.set(f'connection_accepted_{self.session_id}', 'yes')

        # Start sending updates based on iteration count
        if GatheringGamesConsumer.iteration == 1:
            await self._send_updates()  # Send initial updates
            await self._send_updates_gathering()  # Send gathering updates
        else:
            await self._send_updates_gathering()  # Continue gathering updates

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Ensure the session thread exists before attempting to delete it
        task_manager.session_threads[self.session_id][self.name].thread[self.session_id].join()
        
        del task_manager.session_threads[self.session_id]

        # Remove connection from WebSocket group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        
        print(f"WebSocket connection closed for session {self.session_id}", flush=True)

    async def receive(self, text_data):
        """Handle messages received from WebSocket."""
        print("Receive method triggered")
        
        data = json.loads(text_data)
        action = data.get('action')
        reason = data.get('reason')
        session_id = data.get('session_id')

        # Reset iteration if the WebSocket connection is refreshed
        if action == 'close' and reason == 'on_refresh':
            GatheringGamesConsumer.iteration = 0
            print(GatheringGamesConsumer.iteration)

    async def _send_updates(self):        
        """Continuously send updates on progress until stop_event_var is set."""
        
        # Retrieve min and max progress values from Redis
        if (int(redis_buffer_instance.redis_1.get(f'min_{self.session_id}').decode('utf-8')) != -1) and \
           (int(redis_buffer_instance.redis_1.get(f'max_{self.session_id}').decode('utf-8')) != -1):
            from_min = int(redis_buffer_instance.redis_1.get(f'min_{self.session_id}').decode('utf-8'))
            from_max = int(redis_buffer_instance.redis_1.get(f'max_{self.session_id}').decode('utf-8'))
        else:
            from_min = None
            from_max = None

        while True:
            if from_min is not None and from_max is not None:
                await self._send_progress_update(from_min, from_max)

            print("In _send_updates...")

            # Check if the stop event is triggered
            if self._should_stop():
                await asyncio.sleep(0.2)
                break

            await asyncio.sleep(0.1)  # Adjust interval as needed
       
    async def _send_updates_gathering(self):     
        """Continuously send updates for gathering game data."""
        task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"].clear()   
        redis_buffer_instance.redis_1.set(f'shared_progress_gathering_{self.session_id}', '-1')
        self.stop_event_var = False

        while True:
            # Retrieve progress value from Redis
            progress = int(float(redis_buffer_instance.redis_1.get(f'shared_progress_gathering_{self.session_id}').decode('utf-8')))
            
            if progress is not None:
                if progress >= 100:
                    progress = 100
                if progress >= 0:
                    progress_data = {f'progress_gathering_games_{self.session_id}': str(progress)}
                    print(f"Progress data to send: {progress_data}")
                    progress_to_send = f'progress_gathering_games_{self.session_id}'
                    await self.send(text_data=json.dumps({str(progress_to_send): str(progress)}))
            
            print("In _send_updates_gathering...")

            # Check if stop event is triggered
            if self._should_stop():
                await asyncio.sleep(0.2)
                break

            await asyncio.sleep(0.2)  # Adjust interval as needed

    async def _send_progress_update(self, from_min, from_max):
        """Retrieve and send mapped progress value."""
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
                await self.send(text_data=json.dumps({str(progress_to_send): str(mapped_progress)}))

    def _map_progress(self, progress, from_min, from_max):
        """Map progress value to a 0-100 scale.""" 
        if progress != 0:
            progress_when_fast = int(redis_buffer_instance.redis_1.get(f'prog_when_fast_{self.session_id}').decode('utf-8'))
            if progress_when_fast == 100:
                progress = from_max  # Set to maximum progress
                redis_buffer_instance.redis_1.set('prog_when_fast', '-1')  # Reset the fast flag
            return int(self._scale_value(progress, from_min, from_max, 0, 100))
        return 0

    def _scale_value(self, value, from_min, from_max, to_min, to_max):
        """Scale a value from one range to another."""
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

    def _should_stop(self):
        """Check if the stop event is triggered."""
        if task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"].is_set():
            print(task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"])
            self.stop_event_var = True

        return self.stop_event_var
