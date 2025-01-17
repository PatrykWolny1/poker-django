import json
from home.redis_buffer_singleton import redis_buffer_instance_one_pair_game
class Node(object):
    
    def __init__(self, name: str, visited: bool = False, amount: int = 0, exchange: str = None, player_index = None, session_id = None):
        self.name = name
        
        self.branches = []
        self.internal_nodes = []
        self.leaf_nodes = []
        
        self.visited = visited
        self.amount = amount
        self.exchange = exchange
        self.redis = redis_buffer_instance_one_pair_game.redis_1
        self.session_id = session_id
        self.player_index = player_index
            
    def __str__(self) -> str:
        str_result = ''

        # ROOT
        str_result = '\t'*5 + self.name
        
        str_result += '\n'*2
        
        # ExchangeCards?
        str_result += '\t'*4 + ' '*4 + str(self.internal_nodes[0][0])

        str_result += '\n'*2
        
        # Branches p(x) 1   p(x) 2 
        for idx in range(0, len(self.internal_nodes[0][0].branches)):
            str_result += '\t'*3 + str(self.internal_nodes[0][0].branches[idx])
            self.redis.set(f'p1_2x_{idx}_{self.player_index}_{self.session_id}', str(self.internal_nodes[0][0].branches[idx]))

        str_result += '\n'
        
        # No 
        if self.exchange == 'n' or self.visited == False:
            str_result += (('\t'*3) if self.visited == False else ('\t'*3)) + ' '*2 + str(self.internal_nodes[0][0].leaf_nodes[0])
            if self.visited:
                self.redis.set(f'yes_no_{self.player_index}_{self.session_id}', str(self.internal_nodes[0][0].leaf_nodes[0]))
            
        
        # Yes
        if self.exchange == 't' or self.visited == False:
            str_result += (('\t'*3) if self.visited == False else ('\t'*6)) + ' '*2 + str(self.internal_nodes[1][0])
            if self.visited:
                self.redis.set(f'yes_no_{self.player_index}_{self.session_id}', str(self.internal_nodes[1][0]))
        
        str_result += '\n'
        
        # P1(x)
        str_result += '\t'*5 + str(self.internal_nodes[1][0].branches[0])
        self.redis.set(f'p1x_{self.player_index}_{self.session_id}', str(self.internal_nodes[1][0].branches[0]))
        
        # P2(x)
        str_result += '\t'*3 + str(self.internal_nodes[1][0].branches[1])
        self.redis.set(f'p2x_{self.player_index}_{self.session_id}', str(self.internal_nodes[1][0].branches[1]))
        
        str_result += '\n'

        # Two Cards
        if self.amount == 2 or self.visited == False:
            str_result += (('\t'*5) if self.visited == False else ('\t'*5)) + str(self.internal_nodes[1][0].leaf_nodes[0])
            if self.visited:
                self.redis.set(f'cards_2_3_{self.player_index}_{self.session_id}', str(self.internal_nodes[1][0].leaf_nodes[0]))
        
        # Three Cards
        if self.amount == 3 or self.visited == False:
            str_result += (('\t'*3) if self.visited == False else ('\t'*9)) + str(self.internal_nodes[1][0].leaf_nodes[1])
            if self.visited:
                self.redis.set(f'cards_2_3_{self.player_index}_{self.session_id}', str(self.internal_nodes[1][0].leaf_nodes[1]))
        
        if self.amount == 0:
            if self.visited:
                self.redis.set(f'cards_2_3_{self.player_index}_{self.session_id}', '0')

        # Add the event to a Redis list
        event = {
            "player_index" : self.player_index,
            "tree": "data_ready"
        }

        self.redis.rpush(f"game_queue_{self.session_id}", json.dumps(event))
                                                      
        return str_result
