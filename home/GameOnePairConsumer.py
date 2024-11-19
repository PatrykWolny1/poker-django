from channels.generic.websocket import AsyncWebsocketConsumer
from home.redis_buffer_singleton import redis_buffer_instance_one_pair_game, redis_buffer_instance_stop, redis_buffer_instance
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
        await self._send_updates_info_cards()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        print("WebSocket connection closed")
        redis_buffer_instance_one_pair_game.redis_1.flushdb()
        task_manager.stop_event.set()
        await self.close()

    async def receive(self, text_data):
        """Handle messages received from WebSocket (currently not used)."""
        pass
    
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
        redis_buffer_instance_one_pair_game.redis_1.set('player_number', '0')
        redis_buffer_instance_one_pair_game.redis_1.set('wait_buffer', '0')


        # for player in range(0, 2):
        #     redis_buffer_instance_one_pair_game.redis_1.delete(f'arr_{player}')
        #     redis_buffer_instance_one_pair_game.redis_1.delete(f'cards_{player}')
            
        # redis_buffer_instance_one_pair_game.redis_1.set('player_number', '0')
        # redis_buffer_instance_one_pair_game.redis_1.set('wait_buffer', '0')
        # redis_buffer_instance_one_pair_game.redis_1.delete('arrangement')
        # redis_buffer_instance_one_pair_game.redis_1.delete('exchange_cards')
        # redis_buffer_instance_one_pair_game.redis_1.delete('type_arrangement')
        # redis_buffer_instance_one_pair_game.redis_1.delete('chance')
        # redis_buffer_instance_one_pair_game.redis_1.delete('amount')
        # task_manager.stop_event.clear()
    
    async def _send_updates(self):
        
        """Continuously send updates on progress and data script until stop_event_var is set."""
        
        while True:
            with task_manager.cache_lock_event_var:
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

            await asyncio.sleep(0.3)  # Adjust interval as needed
        
        self._initialize_redis()

    async def _send_updates_info_cards(self):
        player_number = 0
        while True:   
            if player_number < 2:
                redis_buffer_instance_one_pair_game.redis_1.set('player_number', str(player_number)) 
                if redis_buffer_instance_one_pair_game.redis_1.get(f'cards_{player_number}') is not None:
                    cards_list = json.loads(redis_buffer_instance_one_pair_game.redis_1.get(f'cards_{player_number}'))   
                    print(cards_list)
                    
                
                    if cards_list is not None:
                        await self.send(text_data=json.dumps({'cards': cards_list}))
                      
                if redis_buffer_instance_one_pair_game.redis_1.get('type_arrangement') is not None:
                    type_arr_str = redis_buffer_instance_one_pair_game.redis_1.get('type_arrangement').decode('utf-8')
                    print(type_arr_str)
                    
                    redis_buffer_instance_one_pair_game.redis_1.set('player_number', str(player_number))   

                    if type_arr_str is not None:
                        await self.send(text_data=json.dumps({'type_arrangement': type_arr_str}))  
                    
                    player_number += 1     
                    redis_buffer_instance_one_pair_game.redis_1.set('player_number', str(player_number)) 

                                                  
                if redis_buffer_instance_one_pair_game.redis_1.get('exchange_cards') is not None:
                    exchange_cards = redis_buffer_instance_one_pair_game.redis_1.get('exchange_cards').decode('utf-8')
                        
                    if exchange_cards is not None:
                        await self.send(text_data=json.dumps({'exchange_cards': exchange_cards})) 
                        redis_buffer_instance_one_pair_game.redis_1.delete('exchange_cards')

             
                
                if (redis_buffer_instance_one_pair_game.redis_1.get('chance') is not None):
                    print(player_number, int(redis_buffer_instance_one_pair_game.redis_1.get('player_number').decode('utf-8')))
                    if player_number != int(redis_buffer_instance_one_pair_game.redis_1.get('player_number').decode('utf-8')):
                        player_number = int(redis_buffer_instance_one_pair_game.redis_1.get('player_number').decode('utf-8')) 
                    redis_buffer_instance_one_pair_game.redis_1.set('player_number', str(player_number))
              
                    chance = redis_buffer_instance_one_pair_game.redis_1.get('chance').decode('utf-8')
                    
                    print(chance)
                    
                    await self.send(text_data=json.dumps({'chances': chance}))
                    redis_buffer_instance_one_pair_game.redis_1.delete('chance')
                    
                if (redis_buffer_instance_one_pair_game.redis_1.get('number_exchange') is not None):   
                                     
                    amount = redis_buffer_instance_one_pair_game.redis_1.get('number_exchange').decode('utf-8')                    

                    if amount is not None:
                        await self.send(text_data=json.dumps({'amount': str(amount)}))
                        redis_buffer_instance_one_pair_game.redis_1.delete('number_exchange')  
                    
                    redis_buffer_instance_one_pair_game.redis_1.set('player_number', str(player_number))
                    player_number += 1  

            if redis_buffer_instance_one_pair_game.redis_1.get('player_number').decode('utf-8') == '2':
                redis_buffer_instance_one_pair_game.redis_1.flushdb()
                # for player in range(0, 2):
                #     redis_buffer_instance_one_pair_game.redis_1.delete(f'arr_{player}')
                #     redis_buffer_instance_one_pair_game.redis_1.delete(f'cards_{player}')
                    
                player_number = 0
                redis_buffer_instance_one_pair_game.redis_1.set('player_number', '0')
                redis_buffer_instance_one_pair_game.redis_1.set('wait_buffer', '0')
                redis_buffer_instance.redis_1.set("entered_value", '10982') #one_pair 1098240
                # redis_buffer_instance_one_pair_game.redis_1.delete('arrangement')
                # redis_buffer_instance_one_pair_game.redis_1.delete('exchange_cards')
                # redis_buffer_instance_one_pair_game.redis_1.delete('type_arrangement')
                # redis_buffer_instance_one_pair_game.redis_1.delete('chance')
                # redis_buffer_instance_one_pair_game.redis_1.delete('amount')
                
                while redis_buffer_instance_one_pair_game.redis_1.get('wait_buffer').decode('utf-8') == '0':
                    print("IN CONSUMER")
                    await asyncio.sleep(1)          
                if redis_buffer_instance_one_pair_game.redis_1.get('wait_buffer').decode('utf-8') == '1':
                    redis_buffer_instance_one_pair_game.redis_1.set('wait_buffer', '0')
            await asyncio.sleep(2)
    
    async def _send_progress_update(self, from_min, from_max):
        """Retrieve and send mapped progress value."""
        # Only lock the part where progress is fetched
        with task_manager.cache_lock_progress:
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