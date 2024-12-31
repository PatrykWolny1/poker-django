from channels.generic.websocket import AsyncWebsocketConsumer
from home.redis_buffer_singleton import redis_buffer_instance_one_pair_game, redis_buffer_instance_stop, redis_buffer_instance
from home.ThreadVarManagerSingleton import task_manager
from home.views import session_threads
from home.MyThread import MyThread
from threading import Event
import json
import asyncio
import time
import logging
import sys
import signal
import os
import redis
from asyncio import Queue
from asgiref.sync import sync_to_async
from urllib.parse import parse_qs
logger = logging.getLogger(__name__)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
connected_sessions = {}

count = 0
redis_client = redis_buffer_instance_one_pair_game.redis_1

class GameOnePairConsumer(AsyncWebsocketConsumer):   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Register signal handlers for SIGINT (CTRL+C) and SIGTSTP (CTRL+Z)
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGABRT, self.handle_signal)
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
        finally:
            print("send_from_queue task exiting")
    async def connect(self):
        global task_manager, session_threads
        """Handle WebSocket connection."""
        global count
        # Parse query string
        # Extract session ID from the query string
        query_string = self.scope.get("query_string", b"").decode()
        self.session_id = query_string.split("=")[-1] if "=" in query_string else None
        # self.session_id = str(query_params.get("session_id", [None])[0])


        if not self.session_id:
            print("No session ID provided. Closing WebSocket.")
            await self.close()
            return

        print(f"WebSocket connected with session ID: {self.session_id}")

        print("Attempting to accept WebSocket connection...", flush=True)
        await self.accept()
        print("WebSocket connection accepted", flush=True)

        # Wait for the thread to initialize
        retries = 30
        while self.session_id not in session_threads and retries > 0:
            print(f"Waiting for session thread initialization for {self.session_id}...")
            await asyncio.sleep(0.5)  # Wait for the thread to be initialized
            retries -= 1

        if self.session_id not in session_threads:
            print(f"Session thread for {self.session_id} not initialized. Closing connection.")
            await self.close(code=4001)
            return

        # Clear the stop_event
        session_threads[self.session_id]["stop_event"].clear()
        print(session_threads)
        task_manager.stop_event.clear()
        task_manager.stop_event_main.clear()
        session_threads[self.session_id]["stop_event"].clear()
        print(session_threads[self.session_id]["stop_event"].is_set())
        self._initialize_redis()

        self.queue = asyncio.Queue()

        self.send_task = asyncio.create_task(self.send_from_queue())

        redis_buffer_instance_one_pair_game.redis_1.set(f'connection_accepted_{self.session_id}', 'yes')

        print("Count: ", count, flush=True)

        # while not task_manager.stop_event_main.is_set():
        #     break_flag = redis_buffer_instance_one_pair_game.redis_1.get('thread_status').decode('utf-8')
        #     if break_flag == 'ready':
        #         print("Received 'ready' message from Redis Pub/Sub.", flush=True)
        #         break
        #     if redis_buffer_instance_one_pair_game.redis_1.get('stop_event_send_updates').decode('utf-8') == '1':
        #         break
        #     await asyncio.sleep(0.1)

        await self._send_updates()
        count += 1
        await self.listen_to_redis_queue()

    async def listen_to_redis_queue(self):
        global task_manager, session_threads
        """Process messages from the Redis queue."""

        while self.session_id in session_threads and not session_threads[self.session_id]["stop_event"].is_set():
            try:
                # Block until a message is available in the list or timeout
                result = redis_client.blpop(f"game_queue_{self.session_id}", timeout=1)  # Returns None if no message
                if result is None:
                    # No message in the queue within the timeout
                    await asyncio.sleep(0.1)  # Yield control to the event loop
                    continue

                # Unpack the result (result is not None here)
                _, message_data = result
                print("Raw message:", message_data)

                # Decode and process the message
                message_data = message_data.decode('utf-8')
                data = json.loads(message_data)
                print("Decoded data:", data)

                if data["event"] == "data_ready":
                    player_index = str(data["player_index"])
                    
                    # session_id = self.scope["session"].session_key

                    # Retrieve additional data from Redis
                    cards_key = f'cards_{player_index}_{self.session_id}'
                    type_arr_key = f'type_arrangement_{player_index}_{self.session_id}'
                    print(cards_key, "CARDS KEY##################")
                    cards_data = redis_client.get(cards_key)
                    type_arr_data = redis_client.get(type_arr_key)

                    if cards_data and type_arr_data:
                        cards_list = json.loads(cards_data.decode('utf-8'))
                        type_arr_str = type_arr_data.decode('utf-8')
                        # Send data to the WebSocket client
                        await self.queue_message({
                            f"type_arrangement_{self.session_id}": type_arr_str,
                            f"cards_{self.session_id}": cards_list
                        })
            except json.JSONDecodeError as e:
                print("JSON decode error:", e)
            except Exception as e:
                print("Unexpected error:", e)


    async def disconnect(self, close_code):
        print("WebSocket connection closed", flush=True)
        # redis_buffer_instance_one_pair_game.redis_1.publish('thread_status', 'disconnect')
        # redis_buffer_instance_one_pair_game.redis_1.set('stop_event_send_updates', '1')
        # session_id = self.scope["session"].session_key
        # if session_id in connected_sessions:
        #     connected_sessions[session_id].remove(self)
        #     if not connected_sessions[session_id]:
        #         del connected_sessions[session_id]
        # print(f"WebSocket disconnected for instance: {self.session_id}", flush=True)

        # # Remove the user from the group
        # await self.channel_layer.group_discard(
        #     self.group_name,
        #     self.channel_name
        # )
        print(f"WebSocket disconnected. Session ID: {self.session_id}, Close Code: {close_code}", flush=True)
        try:
            if self.send_task:
                print(f"Cancelling task {self.send_task}", flush=True)
                self.send_task.cancel()
                try:
                    await self.send_task
                except asyncio.CancelledError:
                    print("send_from_queue task cancelled")
        finally:
            print("Disconnect cleanup complete", flush=True)

        count = 0

        # Additional cleanup if needed
        # E.g., stop tasks, flags, or shared resources associated with this session

        print("Cleanup completed for session:", self.session_id)
        print(f"Disconnected session: {self.session_id}", flush=True)
        await super().disconnect(close_code)
                
    async def receive(self, text_data):
        global count
        """Handle messages received from WebSocket (currently not used)."""
        print("Receive method triggered")
        data = json.loads(text_data)
        if data['action'] == 'close':
            reason = data['reason']
            if reason == 'on_refresh':
                print("ON REFRESH$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$", flush=True)
                task_manager.stop_event.set()
                task_manager.stop_event_main.set()
                redis_buffer_instance_one_pair_game.redis_1.set('on_refresh', '1')
                try:
                    if self.send_task:
                        print(f"Cancelling task {self.send_task}", flush=True)
                        self.send_task.cancel()
                        try:
                            await self.send_task
                        except asyncio.CancelledError:
                            print("send_from_queue task cancelled")
                finally:
                    print("Disconnect cleanup complete", flush=True)

                count = 0
            elif reason == 'button_click':
                redis_buffer_instance_one_pair_game.redis_1.set('on_refresh', '0')
                count += 1
    
    def handle_signal(self, sig, frame):
        """Handle signals (SIGINT and SIGTSTP)."""
        print(f"Signal {sig} received, cleaning up...")
        # Close WebSocket connection

        redis_buffer_instance_one_pair_game.redis_1.set('stop_event_send_updates', '1')
        task_manager.stop_event.set()
                
        # Schedule asynchronous cleanup
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(self.async_cleanup())
        else:
            loop.run_until_complete(self.async_cleanup())
        
        print("Exiting gracefully...") 
        
        # Perform any additional cleanup if necessary
        os._exit(0)
    async def cleanup(self):
        print("Performing cleanup...", flush=True)
        task_manager.stop_event.set()
        task_manager.stop_event_main.set()
        # Cancel the send_from_queue task
        if self.send_task:
            self.send_task.cancel()
            try:
                await asyncio.wait_for(self.send_task, timeout=5)
            except asyncio.TimeoutError:
                print("send_task did not finish in time")
    async def async_cleanup(self):
        """Handle asynchronous cleanup."""
        
        print("Starting asynchronous cleanup...")
        await self.disconnect(close_code=1000)
        print("Asynchronous cleanup complete.")
        
    def _initialize_redis(self):
        """Initialize Redis values for shared progress and stop event."""
        redis_buffer_instance.redis_1.set(f'shared_progress_{self.session_id}', '0')
        redis_buffer_instance.redis_1.set('stop_event_var', '0')
        redis_buffer_instance.redis_1.set('prog_when_fast', '-1')  # Reset the fast flag
        redis_buffer_instance.redis_1.set('choice_1', '2')
        redis_buffer_instance.redis_1.set('choice', '2')
        redis_buffer_instance.redis_1.set('when_one_pair', '1')
        redis_buffer_instance.redis_1.set("entered_value", '10982') #one_pair 1098240
        redis_buffer_instance.redis_1.set('game_si_human', '2')
        for player in range(0, 2):
            redis_buffer_instance_one_pair_game.redis_1.delete(f'cards_{player}')
        redis_buffer_instance_one_pair_game.redis_1.delete('strategy')
        redis_buffer_instance_one_pair_game.redis_1.set('player_number', '0')
        redis_buffer_instance_one_pair_game.redis_1.set('wait_buffer', '0')
        redis_buffer_instance_one_pair_game.redis_1.set('stop_event_send_updates', '0')
    
    async def _send_updates(self):
        
        """Continuously send updates on progress and data script until stop_event_var is set."""

        while not task_manager.stop_event.is_set():
            with task_manager.cache_lock_event_var:
                print(redis_buffer_instance.redis_1.get(f'min_{self.session_id}'), redis_buffer_instance.redis_1.get(f'max_{self.session_id}'), "MINMAX")
                if (redis_buffer_instance.redis_1.get(f'min_{self.session_id}') is not None) and redis_buffer_instance.redis_1.get(f'max_{self.session_id}') is not None:
                    from_min = int(redis_buffer_instance.redis_1.get(f'min_{self.session_id}').decode('utf-8'))
                    from_max = int(redis_buffer_instance.redis_1.get(f'max_{self.session_id}').decode('utf-8'))
                else:
                    from_min = None
                    from_max = None
        
            if from_min is not None and from_max is not None:
                await self._send_progress_update(from_min, from_max)

            if self._should_stop():
                break
            
            print("In _send_updates()")
            
            await asyncio.sleep(0.2)  # Adjust interval as needed
    
    async def _send_updates_info_cards(self):
        global count 
        """Send updates for info cards and related data in real-time."""
        print("Begin: _send_updates_info_cards")
        task_manager.stop_event.clear()
        player_number = 0

        redis = redis_buffer_instance_one_pair_game.redis_1

        while redis.get('stop_event_send_updates') and redis.get('stop_event_send_updates').decode('utf-8') == '0':
            # Update player number in Redis
            # print(player_number)
            print("In _send_updates_info_cards")

            if player_number < 2:
                redis.set('player_number', str(player_number))
                
                # Handle player cards
                await self._process_player_cards(redis, player_number)

                # Handle arrangement type
                player_number = await self._process_type_arrangement(redis, player_number)

                # Handle exchange cards
                await self._process_exchange_cards(redis)

                # Handle chance data
                await self._process_chances(redis)

                # Handle number of exchanges
                player_number = await self._process_number_exchanges(redis, player_number)
                
                await self._process_player_cards_result(redis, player_number)

                player_number = await self._process_type_arrangement_result(redis, player_number)
                # print(player_number)
                # Check if stop event is triggered
                if redis.get('stop_event_send_updates') and redis.get('stop_event_send_updates').decode('utf-8') == '1':
                    print("Return from _send_updates_info_cards()...")
                    await self.disconnect(close_code=1000)
                    return

            # Reset player data after processing
            if (redis.get('player_number') and redis.get('player_number').decode('utf-8') == '2'):
                self._reset_player_data(redis)
                player_number = 0

            strategy_key = 'strategy'
            if redis.get(strategy_key) is not None:
                p1_2x_1_key = []
                
                yes_no_key = 'yes_no'
                for number in range(2):
                    p1_2x_1_key.append(f'p1_2x_{number}')
                p1x_key = 'p1x'
                p2x_key = 'p2x'
                cards_2_3_key = 'cards_2_3'
                first_second_key = 'first_second'
                
                p1_2x_1 = []
                
                no_strategy = redis.get(strategy_key).decode('utf-8')
                for number in range(2):
                    p1_2x_1.append(redis.get(p1_2x_1_key[number]).decode('utf-8'))
                yes_no = redis.get(yes_no_key).decode('utf-8')
                p1x = redis.get(p1x_key).decode('utf-8')
                p2x = redis.get(p2x_key).decode('utf-8')
                cards_2_3 = redis.get(cards_2_3_key).decode('utf-8')
                first_second = redis.get(first_second_key).decode('utf-8')

                print(no_strategy, "STRATEGY")
                                
                if no_strategy is not None:
                    if no_strategy == '0':
                        for number in range(2):
                            await self.send(text_data=json.dumps({f'p1_2x_{number}': p1_2x_1[number]}))
                        await self.send(text_data=json.dumps({'yes_no': yes_no}))
                        await self.send(text_data=json.dumps({'p1x': p1x}))
                        await self.send(text_data=json.dumps({'p2x': p2x}))
                        await self.send(text_data=json.dumps({'cards_2_3': cards_2_3}))
                        await self.send(text_data=json.dumps({'first_second': first_second}))
                        await self.send(text_data=json.dumps({'strategy_one': no_strategy}))

                    if no_strategy == '1':
                        for number in range(2):
                            await self.send(text_data=json.dumps({f'p1_2x_{number}': p1_2x_1[number]}))
                        await self.send(text_data=json.dumps({'yes_no': yes_no}))
                        await self.send(text_data=json.dumps({'p1x': p1x}))
                        await self.send(text_data=json.dumps({'p2x': p2x}))
                        await self.send(text_data=json.dumps({'cards_2_3': cards_2_3}))
                        await self.send(text_data=json.dumps({'first_second': first_second}))
                        await self.send(text_data=json.dumps({'strategy_two': no_strategy}))
                        
            await asyncio.sleep(0.1)

    async def _process_player_cards(self, redis, player_number):
        """Process and send player cards."""
        cards_key = f'cards_{player_number}'
        cards_data = redis.get(cards_key)

        if cards_data is not None:
            cards_list = json.loads(cards_data)
            if cards_list:
                print(cards_list)
                await self.send(text_data=json.dumps({'cards': cards_list}))

    async def _process_type_arrangement(self, redis, player_number):
        """Process and send type arrangement."""
        type_arr_data = redis.get('type_arrangement')
        if type_arr_data is not None:
            type_arr_str = type_arr_data.decode('utf-8')
               
            if type_arr_str:
                await self.send(text_data=json.dumps({'type_arrangement': type_arr_str}))
                redis.delete('type_arrangement')
                
            player_number += 1   
            redis.set('player_number', str(player_number))
            return player_number
        return player_number

    async def _process_exchange_cards(self, redis):
        """Process and send exchange cards."""
        exchange_data = redis.get('exchange_cards')
        if exchange_data is not None:
            exchange_cards = exchange_data.decode('utf-8')
            if exchange_cards:
                await self.send(text_data=json.dumps({'exchange_cards': exchange_cards}))
                redis.delete('exchange_cards')

    async def _process_chances(self, redis):
        """Process and send chance data."""
        chance_data = redis.get('chance')
        if chance_data is not None:
            chance = chance_data.decode('utf-8')
            await self.send(text_data=json.dumps({'chances': chance}))
            redis.delete('chance')

    async def _process_number_exchanges(self, redis, player_number):
        """Process and send number of exchanges."""
        num_exchanges_data = redis.get('number_exchange')
        if num_exchanges_data is not None:
            num_exchanges = num_exchanges_data.decode('utf-8')
            if num_exchanges:
                await self.send(text_data=json.dumps({'amount': num_exchanges}))
                redis.delete('number_exchange')
            player_number += 1
            redis.set('player_number', str(player_number))
            return player_number
        return player_number
    
    async def _process_player_cards_result(self, redis, player_number):
        """Process and send player cards."""
        cards_key = f'cards_result_{player_number}'
        cards_data = redis.get(cards_key)

        if cards_data is not None:
            cards_list = json.loads(cards_data)
            if cards_list:
                print(cards_list)
                await self.send(text_data=json.dumps({'cards': cards_list}))

    async def _process_type_arrangement_result(self, redis, player_number):
        type_arr_result_data = redis.get('type_arrangement_result')
        if type_arr_result_data is not None:
            type_arr_result_str = type_arr_result_data.decode('utf-8')
            
            if type_arr_result_str:
                await self.send(text_data=json.dumps({'type_arrangement_result': type_arr_result_str}))
                redis.delete('type_arrangement_result')
            
            player_number += 1   
            redis.set('player_number', str(player_number))
            return player_number
        return player_number
    
    def _reset_player_data(self, redis):
        """Reset player data in Redis after processing."""
        for player in range(2):
            redis.delete(f'cards_{player}')
            redis.delete(f'cards_result_{player}')
            
        redis.set('player_number', '0')
        redis.set('wait_buffer', '0')
        redis.set("entered_value", '10982')  # Example value

    async def _send_progress_update(self, from_min, from_max):
        """Retrieve and send mapped progress value."""

        progress = int(redis_buffer_instance_one_pair_game.redis_1.get(f'shared_progress_{self.session_id}').decode('utf-8'))
        mapped_progress = self._map_progress(progress, from_min, from_max)
        
        if mapped_progress is not None:
            if mapped_progress >= 100:
                mapped_progress = 100
            if mapped_progress != 0:
                await self.queue_message({"progress": str(mapped_progress)})
                       
    def _map_progress(self, progress, from_min, from_max):
        """Map and return the progress value to a 0-100 range."""
        if progress != 0:
            if redis_buffer_instance_one_pair_game.redis_1.get('prog_when_fast') is not None:
                progress_when_fast = int(redis_buffer_instance_one_pair_game.redis_1.get('prog_when_fast').decode('utf-8'))
            if progress_when_fast == 100:
                progress = from_max  # Once the condition is met, set to maximum
                redis_buffer_instance_one_pair_game.redis_1.set('prog_when_fast', '-1')  # Reset the fast flag
            return int(self._scale_value(progress, from_min, from_max, 0, 100))
        return 0
    
    def _scale_value(self, value, from_min, from_max, to_min, to_max):
        """Scale a value from one range to another."""
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min
    
    def _should_stop(self):
        """Check if stop event or completion conditions are met."""
        # Only lock around the Redis get operation
        stop_event_var = 0
        with task_manager.cache_lock_event_var:
            if redis_buffer_instance_stop.redis_1.get('stop_event_var') is not None:
                stop_event_var = redis_buffer_instance_stop.redis_1.get('stop_event_var').decode('utf-8')
                
        if stop_event_var == '1':
            task_manager.stop_event.set()

        return stop_event_var == '1'