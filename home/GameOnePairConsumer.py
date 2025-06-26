from channels.generic.websocket import AsyncWebsocketConsumer
from home.redis_buffer_singleton import redis_buffer_instance_one_pair_game, redis_buffer_instance
from home.ThreadVarManagerSingleton import task_manager
from home.MyThread import MyThread
from threading import Event
import json
import asyncio
import signal
import os
from asyncio import Queue
from asgiref.sync import sync_to_async
from urllib.parse import parse_qs

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

redis_client = redis_buffer_instance_one_pair_game.redis_1

class GameOnePairConsumer(AsyncWebsocketConsumer):
    count = 0  # Static variable to keep track of an unspecified count (usage context depends on further details not shown here)
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Initialize superclass

        # Register signal handlers for graceful shutdown or interruption
        signal.signal(signal.SIGINT, self.handle_signal)  # Handle Ctrl+C
        signal.signal(signal.SIGABRT, self.handle_signal)  # Handle abort signals

        # Initialize the message queue for storing messages before sending them asynchronously
        self.outgoing_message_queue = asyncio.Queue()
        self.send_task = None  # Placeholder for the asyncio task that will handle sending messages

        # Internal attributes for managing state
        self.name = "thread_one_pair_game"
        self.session_id = None  # Session ID will be determined when a connection is established
        self.stop_event_var = False  # A flag to indicate whether to stop the task
        self.count = 1  # Instance variable to track some state, incremented or reset in methods

    async def queue_message(self, data):
        """Add a message to the outgoing queue to be sent later."""
        await self.outgoing_message_queue.put(data)

    async def send_from_queue(self):
        """Continuously take messages from the queue and send them to the WebSocket client."""
        try:
            while True:
                data = await self.outgoing_message_queue.get()  # Wait for a message from the queue
                try:
                    await self.send(text_data=json.dumps(data))  # Send the message as JSON
                    print("Sent message:", data)
                except Exception as e:
                    print("Error sending message:", e)  # Handle exceptions during send
        except asyncio.CancelledError:
            print("send_from_queue task cancelled")  # Handle cancellation of the send task
            raise  # Reraise the exception to propagate cancellation
        finally:
            print("send_from_queue task exiting")  # Cleanup or logging before exit

    async def connect(self):
        """Handle incoming WebSocket connection requests."""
        query_string = self.scope.get("query_string", b"").decode()  # Decode query string from binary
        self.session_id = query_string.split("=")[-1] if "=" in query_string else None  # Extract session ID

        if not self.session_id:
            print("No session ID provided. Closing WebSocket.")
            await self.close()  # Close the connection if no session ID is provided
            return

        await self.accept()  # Accept the WebSocket connection

        # Check if the session ID is known to the task manager, otherwise close the connection
        if self.session_id not in task_manager.session_threads:
            await self.close(code=4001)  # Use a specific close code
            return

        # Initialize Redis and other necessary states for this session
        self._initialize_redis()
        self.queue = asyncio.Queue()  # Re-initialize a local asyncio Queue
        self.send_task = asyncio.create_task(self.send_from_queue())  # Start the sending task

        # Record the acceptance of the connection in Redis
        redis_buffer_instance.redis_1.set(f'connection_accepted_{self.session_id}', 'yes')
        self.count = 0  # Reset or initialize the count
        redis_buffer_instance.redis_1.set(f'when_first_{self.session_id}', self.count)  # Store the count in Redis
        await self._send_updates()  # Start sending updates to the client
        await self.listen_to_redis_queue()  # Begin listening to the Redis queue for this session

    async def listen_to_redis_queue(self):
        global task_manager
        """Process messages from the Redis queue."""
        # Continuously check if the stop event has been set, allowing for graceful termination
        while not task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_croupier"].is_set():
            try:
                # Attempt to pop a message off the Redis queue with a timeout of 1 second
                result = redis_client.blpop(f"game_queue_{self.session_id}", timeout=1)
                if result is None:
                    # If no message is received within the timeout, yield to other tasks
                    await asyncio.sleep(0.1)
                    continue

                # If a message is received, unpack the queue name and the data
                _, message_data = result
                message_data = message_data.decode('utf-8')  # Decode the message data from bytes to string
                data = json.loads(message_data)  # Convert JSON string into a Python dictionary

                # Handling different types of messages based on their identifiers in the data
                if "cards_shuffle" in data and data["cards_shuffle"] == "data_ready":
                    # Process a message indicating shuffled cards are ready to be sent to the client
                    player_index = str(data["player_index"])
                    cards_key = f'cards_{player_index}_{self.session_id}'
                    type_arr_key = f'type_arrangement_{player_index}_{self.session_id}'
                    
                    # Retrieve card data and type arrangement from Redis
                    cards_data = redis_client.get(cards_key)
                    type_arr_data = redis_client.get(type_arr_key)

                    if cards_data and type_arr_data:
                        # If both cards and type data are present, decode and prepare for sending
                        cards_list = json.loads(cards_data.decode('utf-8'))
                        type_arr_str = type_arr_data.decode('utf-8')
                        
                        # Enqueue a message with the card data and type arrangement for the WebSocket client
                        await self.queue_message({
                            f"type_arrangement_{self.session_id}": type_arr_str,
                            f"cards_{self.session_id}": cards_list
                        })

                if "exchange_cards" in data and data["exchange_cards"] == "data_ready":
                    # Handle messages for exchanged cards
                    player_index = str(data["player_index"])
                    exchange_key = f'exchange_cards_{player_index}_{self.session_id}'
                    exchange_data = redis_client.get(exchange_key)

                    if exchange_data:
                        # Send exchange card data to the WebSocket client
                        exchange_cards = exchange_data.decode('utf-8')
                        await self.queue_message({
                            f"exchange_cards_{self.session_id}": exchange_cards
                        })

                if "chance" in data and data["chance"] == "data_ready":
                    # Handle chance calculation results
                    player_index = str(data["player_index"])
                    chance_key = f'chance_{player_index}_{self.session_id}'
                    chance_data = redis_client.get(chance_key)

                    if chance_data:
                        # Send chance data to the WebSocket client
                        chance = chance_data.decode('utf-8')
                        await self.queue_message({
                            f"chances_{self.session_id}": chance
                        })

                if "number_exchange" in data and data["number_exchange"] == "data_ready":
                    # Handle number exchange messages
                    player_index = str(data["player_index"])
                    number_exchange_key = f'number_exchange_{player_index}_{self.session_id}'
                    number_exchange_data = redis_client.get(number_exchange_key)

                    if number_exchange_data:
                        # Send number exchange data to the WebSocket client
                        number_exchange = number_exchange_data.decode('utf-8')
                        await self.queue_message({
                            f"amount_{self.session_id}": number_exchange
                        })

                if "result" in data and data["result"] == "data_ready":
                    # Handle results of the game
                    player_index = str(data["player_index"])
                    cards_result_key = f'cards_result_{player_index}_{self.session_id}'
                    type_arrangement_result_key = f'type_arrangement_result_{player_index}_{self.session_id}'
                    
                    cards_result_data = redis_client.get(cards_result_key)
                    type_arrangement_result_data = redis_client.get(type_arrangement_result_key)

                    if cards_result_data and type_arrangement_result_data:
                        # Prepare and send the result data to the WebSocket client
                        cards_result = json.loads(cards_result_data.decode('utf-8'))
                        type_arrangement_result = type_arrangement_result_data.decode('utf-8')
                        
                        await self.queue_message({
                            f"cards_{self.session_id}": cards_result,
                            f"type_arrangement_result_{self.session_id}": type_arrangement_result
                        })

                if "first_second" in data and data["first_second"] == "data_ready":
                    # Handle 'first_second' messages indicating who goes first or second in the game
                    player_index = str(data["player_index"])
                    first_second_key = f'first_second_{player_index}_{self.session_id}'
                    first_second_data = redis_client.get(first_second_key)

                    if first_second_data:
                        # Send first or second turn information to the WebSocket client
                        first_second = first_second_data.decode('utf-8')
                        await self.queue_message({
                            f"first_second_{self.session_id}": first_second
                        })

                if "tree" in data and data["tree"] == "data_ready":
                    # Handle tree-based decision messages
                    player_index = str(data["player_index"])
                    p1_2x_1_key = [f'p1_2x_{number}_{player_index}_{self.session_id}' for number in range(2)]
                    yes_no_key = f'yes_no_{player_index}_{self.session_id}'
                    p1x_key = f'p1x_{player_index}_{self.session_id}'
                    p2x_key = f'p2x_{player_index}_{self.session_id}'
                    cards_2_3_key = f'cards_2_3_{player_index}_{self.session_id}'

                    # Retrieve and process strategy-related data from Redis
                    p1_2x_1 = [redis_client.get(key).decode('utf-8') for key in p1_2x_1_key]
                    yes_no = redis_client.get(yes_no_key).decode('utf-8')
                    p1x = redis_client.get(p1x_key).decode('utf-8')
                    p2x = redis_client.get(p2x_key).decode('utf-8')
                    cards_2_3 = redis_client.get(cards_2_3_key).decode('utf-8')

                    strategy_key = f'strategy_{player_index}_{self.session_id}'
                    strategy = redis_client.get(strategy_key).decode('utf-8')

                    # Build the message based on strategy and send it to the WebSocket client
                    message = {
                        f"yes_no_{self.session_id}": yes_no,
                        f"p1x_{self.session_id}": p1x,
                        f"p2x_{self.session_id}": p2x,
                        f"cards_2_3_{self.session_id}": cards_2_3,
                    }

                    if strategy == '0' or strategy == '1':
                        for number in range(2):
                            message[f'p1_2x_{number}_{self.session_id}'] = p1_2x_1[number]
                        # message[f'strategy_{strategy}_{self.session_id}'] = strategy
                        redis_client.delete(strategy_key)
                    # Send the prepared message
                    await self.queue_message({strategy_key: message})
                await asyncio.sleep(0.1)

            except json.JSONDecodeError as e:
                print("JSON decode error:", e)  # Handle JSON decoding errors gracefully
            except Exception as e:
                print("Unexpected error:", e)  # Catch all unexpected exceptions

    async def reset_state(self):
        """Reset the state of the WebSocket consumer."""
        if self.send_task:
            print(f"Cancelling task {self.send_task}", flush=True)
            self.send_task.cancel()  # Attempt to cancel the ongoing send task
            try:
                await self.send_task  # Wait for the task to actually cancel
            except asyncio.CancelledError:
                print("send_from_queue task cancelled")  # Confirm cancellation

        # Clear any set events to reset the state for clean processing
        task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_progress"].clear()
        task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_croupier"].clear()

        self._initialize_redis()  # Reinitialize Redis connection or states

        self.send_task = asyncio.create_task(self.send_from_queue())  # Restart the sending task
        await self.listen_to_redis_queue()  # Restart listening to the Redis queue for new messages
        self.count += 1  # Increment the count for internal tracking
        redis_buffer_instance.redis_1.set(f'when_first_{self.session_id}', self.count)  # Update the count in Redis

    async def disconnect(self, close_code):
        """Handle disconnection of the WebSocket."""
        if hasattr(self, "send_task") and not self.send_task.done():
            self.send_task.cancel()  # Cancel the send task if it's still running
            try:
                await self.send_task  # Wait for the cancellation to complete
            except asyncio.CancelledError:
                print("send_from_queue task successfully cancelled during disconnect")
            finally:
                print("send_from_queue task cleanup completed")  # Confirm cleanup

        print("Disconnect cleanup complete", flush=True)
        print(f"WebSocket disconnected. Session ID: {self.session_id}, Close Code: {close_code}", flush=True)
        await super().disconnect(close_code)  # Call the superclass method to handle additional disconnection logic

    async def receive(self, text_data):
        """Handle incoming messages from the WebSocket client."""
        print("Receive method triggered")  # Log that the receive method was called

        data = json.loads(text_data)  # Parse the received JSON text data
        action = data.get('action')  # Extract action to determine how to respond
        reason = data.get('reason')  # Extract reason for action
        session_id = data.get('session_id')  # Extract session ID from message

        if action == 'close':
            if reason == 'on_refresh':
                print("Consumer One Pair Game - on refresh")
                # Set stop events on refresh to halt current operations
                task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_progress"].set()
                task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_croupier"].set()
                if self.send_task:
                    print(f"Cancelling task {self.send_task}", flush=True)
                    self.send_task.cancel()  # Cancel the send task
                await self.close()  # Close the WebSocket connection
                return

            elif reason == 'button_click':
                print("Button click reason received", flush=True)
                redis_buffer_instance_one_pair_game.redis_1.set('on_refresh', '0')  # Reset refresh state in Redis
                # Clear stop events to allow new actions
                task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_progress"].clear()
                task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_croupier"].clear()
                print("BEFORE ERR: ", self.session_id, flush=True)

                self.session_id = session_id  # Update the session ID

                self.count = int(redis_buffer_instance.redis_1.get(f'when_first_{self.session_id}').decode('utf-8'))  # Get the current count from Redis

                print(self.count, "RESETTING VIA BUTTON CLICK!", self.session_id)
                await self.reset_state()  # Reset the state based on button click
                return
        else:
            print("Unknown action received:", action)  # Log if an unrecognized action is received

    def handle_signal(self, sig, frame):
        """Respond to system signals like SIGINT (Ctrl+C) and SIGABRT."""
        print(f"Signal {sig} received, cleaning up...")
        # Signal the application to stop updating and proceed with a cleanup.
        redis_buffer_instance_one_pair_game.redis_1.set('stop_event_send_updates', '1')
        task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_progress"].set()
        task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_croupier"].set()

        # Asynchronously clean up if the event loop is running; otherwise, run the cleanup synchronously.
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(self.async_cleanup())
        else:
            loop.run_until_complete(self.async_cleanup())

        print("Exiting gracefully...")
        # Exit the process cleanly
        os._exit(0)

    async def cleanup(self):
        """Perform cleanup tasks asynchronously."""
        print("Performing cleanup...", flush=True)
        # Set the stop events to halt ongoing processes.
        task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_progress"].set()
        task_manager.session_threads[self.session_id]["thread_one_pair_game"].event["stop_event_croupier"].set()

        # Attempt to cancel the ongoing message-sending task.
        if self.send_task:
            self.send_task.cancel()
            try:
                await asyncio.wait_for(self.send_task, timeout=5)  # Give the task some time to cancel properly.
            except asyncio.TimeoutError:
                print("send_task did not finish in time")  # Log if the task does not cancel in the allotted time.

    async def async_cleanup(self):
        """Execute necessary cleanup operations asynchronously."""
        print("Starting asynchronous cleanup...")
        await self.close()  # Close the WebSocket connection properly.
        print("Asynchronous cleanup complete.")

    def _initialize_redis(self):
        """Initialize or reset Redis data for the current session."""
        # Set initial values or reset existing values in Redis for this session's state management.
        redis_buffer_instance.redis_1.set(f'shared_progress_{self.session_id}', '0')
        redis_buffer_instance.redis_1.set('stop_event_var', '0')
        redis_buffer_instance.redis_1.set('prog_when_fast', '-1')  # Indicates a state where rapid progress needs to be reset.
        redis_buffer_instance.redis_1.set('choice_1', '2')
        redis_buffer_instance.redis_1.set('choice', '2')
        redis_buffer_instance.redis_1.set('when_one_pair', '1')
        redis_buffer_instance.redis_1.set("entered_value", '10982')
        redis_buffer_instance.redis_1.set('game_si_human', '2')

        # Delete card and strategy-related data for each player, resetting the game state.
        for player in range(0, 2):
            redis_buffer_instance_one_pair_game.redis_1.delete(f'cards_{player}')
        redis_buffer_instance_one_pair_game.redis_1.delete('strategy')

        # Reinitialize control values used during gameplay.
        redis_buffer_instance_one_pair_game.redis_1.set('player_number', '0')
        redis_buffer_instance_one_pair_game.redis_1.set('wait_buffer', '0')
        redis_buffer_instance_one_pair_game.redis_1.set('stop_event_send_updates', '0')

    async def _send_updates(self):
        """Continuously check and send updates based on game progress."""
        while True:
            # Fetch min and max values for the progress mapping.
            print(redis_buffer_instance.redis_1.get(f'min_{self.session_id}'), redis_buffer_instance.redis_1.get(f'max_{self.session_id}'), "MINMAX")
            from_min = int(redis_buffer_instance.redis_1.get(f'min_{self.session_id}').decode('utf-8')) if redis_buffer_instance.redis_1.get(f'min_{self.session_id}') is not None else None
            from_max = int(redis_buffer_instance.redis_1.get(f'max_{self.session_id}').decode('utf-8')) if redis_buffer_instance.redis_1.get(f'max_{self.session_id}') is not None else None

            # Send a progress update if valid min and max values are present.
            if from_min is not None and from_max is not None:
                await self._send_progress_update(from_min, from_max)

            # Check if a stop condition has been met to exit the loop.
            if self._should_stop():
                break

            await asyncio.sleep(0.2)  # Small delay to prevent hammering the CPU.

    async def _send_progress_update(self, from_min, from_max):
        """Fetch progress and map it from a raw to a 0-100 scale, then send it."""
        progress = int(redis_buffer_instance_one_pair_game.redis_1.get(f'shared_progress_{self.session_id}').decode('utf-8'))
        mapped_progress = self._map_progress(progress, from_min, from_max)
        
        # Only send progress updates if there's meaningful progress to report.
        if mapped_progress is not None:
            if mapped_progress >= 100:
                mapped_progress = 100
            if mapped_progress != 0:
                await self.queue_message({f"progress_{self.session_id}": str(mapped_progress)})

    def _map_progress(self, progress, from_min, from_max):
        """Convert a raw progress value into a scaled percentage based on specified ranges."""
        if progress != 0:
            progress_when_fast = int(redis_buffer_instance_one_pair_game.redis_1.get('prog_when_fast').decode('utf-8')) if redis_buffer_instance_one_pair_game.redis_1.get('prog_when_fast') is not None else 0
            if progress_when_fast == 100:
                progress = from_max  # Adjust the progress to the max value when a fast progress flag is set.
                redis_buffer_instance_one_pair_game.redis_1.set('prog_when_fast', '-1')  # Reset the fast progress flag.
            return int(self._scale_value(progress, from_min, from_max, 0, 100))
        return 0  # Return 0 if no progress has been made.

    def _scale_value(self, value, from_min, from_max, to_min, to_max):
        """Scale a numerical value from one range to another, linearly transforming it."""
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

    def _should_stop(self):
        """Check whether the conditions to stop updating have been met."""
        # Return true if the stop_event_progress has been set, indicating that updates should cease.
        if task_manager.session_threads[self.session_id][self.name].event["stop_event_progress"].is_set():
            self.stop_event_var = True  # Set the internal stop flag.
        return self.stop_event_var

