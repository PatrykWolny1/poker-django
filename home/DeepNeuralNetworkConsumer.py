from channels.generic.websocket import AsyncWebsocketConsumer
from home.redis_buffer_singleton import redis_buffer_instance
from home.ThreadVarManagerSingleton import task_manager
import json
import asyncio
import time
from urllib.parse import parse_qs
from asgiref.sync import sync_to_async, async_to_sync

class DeepNeuralNetworkConsumer(AsyncWebsocketConsumer):
    iteration = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session_id = None
        self.name = "deep_neural_network"
        self.stop_event_var = False
        self.outgoing_message_queue = asyncio.Queue()  # Initialize the message queue
        self.send_task = None  # Background task for send_from_queue

    async def queue_message(self, data):
        """Add a message to the outgoing queue."""
        await self.outgoing_message_queue.put(data)

    async def send_from_queue(self):
        """Send messages from the outgoing queue."""
        try:
            while True:
                data = await self.outgoing_message_queue.get()
                try:
                    await self.send(text_data=json.dumps(data))
                    print("Sent message:", data)
                except Exception as e:
                    print("Error sending message:", e)
        except asyncio.CancelledError:
            print("send_from_queue task cancelled")
            raise  # Propagate the cancellation to allow proper cleanup
        finally:
            print("send_from_queue task exiting")

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
        
        redis_buffer_instance.redis_1.set(f'fit_output_{self.session_id}', '-1')
        redis_buffer_instance.redis_1.set(f'epoch_percent_{self.session_id}', '-1')
        
        self.queue = asyncio.Queue()

        self.send_task = asyncio.create_task(self.send_from_queue())
        
        while True:
            result = redis_buffer_instance.redis_1.blpop(f"dnn_queue_{self.session_id}", timeout=1)  # Returns None if no message
            if result is None:
                # No message in the queue within the timeout
                await asyncio.sleep(0.1)  # Yield control to the event loop
                continue
            
            # Unpack the result (result is not None here)
            _, message_data = result
            # print("Raw message:", message_data)

            # Decode and process the message
            message_data = message_data.decode('utf-8')
            data = json.loads(message_data)

            if "progress_output" in data and data["progress_output"] == "data_ready":
                await self._send_data_script()

                await self._send_updates_dnn()

            if self._should_stop():
                await asyncio.sleep(0.2)
                break

            await asyncio.sleep(0.001)  # Adjust interval as needed

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if self.session_id in task_manager.session_threads and self.name in task_manager.session_threads:
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
                DeepNeuralNetworkConsumer.iteration = 0
                print(DeepNeuralNetworkConsumer.iteration)
    
    async def _send_data_script(self):
        """Retrieve and send the data script if updated."""
        data_script = redis_buffer_instance.redis_1.get(f'fit_output_{self.session_id}').decode('utf-8')
        # temp_data_script = redis_buffer_instance.redis_1.get(f'fit_output_{self.session_id}').decode('utf-8')

        if data_script != '-1':
            # await self.send(text_data=json.dumps({f'fit_output_{self.session_id}': data_script}))
            await self.queue_message({
                f'fit_output_{self.session_id}': data_script
            })
        

    async def _send_updates_dnn(self):     
        task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"].clear()   
        self.stop_event_var = False

        progress = int(float(redis_buffer_instance.redis_1.get(f'epoch_percent_{self.session_id}').decode('utf-8')))
        
        if progress is not None:
            if progress >= 100:
                progress = 100
            if progress >= 0:
                progress_data = {f'epoch_percent_{self.session_id}': str(progress)}
                print(f"Progress data to send: {progress_data}")
                progress_to_send = f'epoch_percent_{self.session_id}'
                # await self.send(text_data=json.dumps({str(progress_to_send) : str(progress)}))
                await self.queue_message({
                    progress_to_send: str(progress)
                })
        
        print("In _send_updates_dnn...")



    def _should_stop(self):
        """Check if stop event or completion conditions are met."""
        if task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"].is_set():
            print(task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"])
            self.stop_event_var = True

        return self.stop_event_var