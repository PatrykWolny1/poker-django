from channels.generic.websocket import AsyncWebsocketConsumer
from home.redis_buffer_singleton import redis_buffer_instance_one_pair_game, redis_buffer_instance_stop, redis_buffer_instance
from home.ThreadVarManagerSingleton import task_manager
from home.views import task_threads, thread_ids
from home.MyThread import MyThread
import json
import asyncio
import time
import logging
import sys
import signal
import os
logger = logging.getLogger(__name__)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

count = 0

class GameOnePairConsumer(AsyncWebsocketConsumer):   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Register signal handlers for SIGINT (CTRL+C) and SIGTSTP (CTRL+Z)
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGABRT, self.handle_signal)
        
    async def connect(self):
        global count 
        """Handle WebSocket connection."""
        print("Attempting to accept WebSocket connection...", flush=True)
        await self.accept()
        print("WebSocket connection accepted", flush=True) 
        
        redis_buffer_instance_one_pair_game.redis_1.set('connection_accepted', 'yes')

        # Initialize Redis values for shared progress and stop event
        self._initialize_redis()
    
        print("Count: ", count, flush=True)
        if count == 0:
         
            while True:
                break_flag = redis_buffer_instance_one_pair_game.redis_1.get('thread_status').decode('utf-8')
                if break_flag == 'ready':            
                    print("Received 'ready' message from Redis Pub/Sub.", flush=True)
                    break
                if redis_buffer_instance_one_pair_game.redis_1.get('stop_event_send_updates').decode('utf-8') == '1':
                    break
                await asyncio.sleep(0.1)
            await self._send_updates()
            count += 1

        await self._send_updates_info_cards()

    async def disconnect(self, close_code):
        print("WebSocket connection closed", flush=True)
        # redis_buffer_instance_one_pair_game.redis_1.publish('thread_status', 'disconnect')
        redis_buffer_instance_one_pair_game.redis_1.set('stop_event_send_updates', '1')
        task_manager.stop_event.set()
        await super().disconnect(close_code)
                
    async def receive(self, text_data):
        global count
        """Handle messages received from WebSocket (currently not used)."""
        print("Receive method triggered")
        data = json.loads(text_data)
        print(data, "IN RECEIVE")
        
        if data['action'] == 'close':
            reason = data['reason']
            if reason == 'on_refresh':
                redis_buffer_instance_one_pair_game.redis_1.set('on_refresh', '0')
                count = 0
            elif reason == 'button_click':
                redis_buffer_instance_one_pair_game.redis_1.set('on_refresh', '1')
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
    
    async def async_cleanup(self):
        """Handle asynchronous cleanup."""
        
        print("Starting asynchronous cleanup...")
        await self.disconnect(close_code=1000)
        print("Asynchronous cleanup complete.")
        
    def _initialize_redis(self):
        """Initialize Redis values for shared progress and stop event."""
        redis_buffer_instance.redis_1.set('shared_progress', '0')
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
        task_manager.stop_event.clear()
    
    async def _send_updates(self):
        
        """Continuously send updates on progress and data script until stop_event_var is set."""

        while not task_manager.stop_event.is_set():
            with task_manager.cache_lock_event_var:
                print(redis_buffer_instance.redis_1.get('min'), redis_buffer_instance.redis_1.get('max'), "MINMAX")
                if (redis_buffer_instance.redis_1.get('min') is not None) and redis_buffer_instance.redis_1.get('max') is not None:
                    from_min = int(redis_buffer_instance.redis_1.get('min').decode('utf-8'))
                    from_max = int(redis_buffer_instance.redis_1.get('max').decode('utf-8'))
                else:
                    from_min = None
                    from_max = None
        
            if from_min is not None and from_max is not None:
                await self._send_progress_update(from_min, from_max)

            if self._should_stop():
                break
            
            print("In _send_updates()")
            
            await asyncio.sleep(0.5)  # Adjust interval as needed
    
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
        # Only lock the part where progress is fetched
        # with task_manager.cache_lock_progress:
        progress = int(redis_buffer_instance_one_pair_game.redis_1.get('shared_progress').decode('utf-8'))
        mapped_progress = self._map_progress(progress, from_min, from_max)

        if mapped_progress is not None:
            if mapped_progress >= 100:
                mapped_progress = 100
            if mapped_progress != 0:
                await self.send(text_data=json.dumps({'progress': str(mapped_progress)}))
                       
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