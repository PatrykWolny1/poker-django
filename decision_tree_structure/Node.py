from home.redis_buffer_singleton import redis_buffer_instance_one_pair_game
class Node(object):
    
    def __init__(self, name: str, visited: bool = False, amount: int = 0, exchange: str = None):
        self.name = name
        
        self.branches = []
        self.internal_nodes = []
        self.leaf_nodes = []
        
        self.visited = visited
        self.amount = amount
        self.exchange = exchange
        self.redis = redis_buffer_instance_one_pair_game.redis_1
            
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
            self.redis.set(f'p1_2x_{idx}', str(self.internal_nodes[0][0].branches[idx]))
        
        str_result += '\n'
        
        # No 
        if self.exchange == 'n' or self.visited == False:
            str_result += (('\t'*3) if self.visited == False else ('\t'*3)) + ' '*2 + str(self.internal_nodes[0][0].leaf_nodes[0])
            if self.visited:
                self.redis.set('yes_no', str(self.internal_nodes[0][0].leaf_nodes[0]))
            
        
        # Yes
        if self.exchange == 't' or self.visited == False:
            str_result += (('\t'*3) if self.visited == False else ('\t'*6)) + ' '*2 + str(self.internal_nodes[1][0])
            if self.visited:
                self.redis.set('yes_no', str(self.internal_nodes[1][0]))
        
        str_result += '\n'
        
        # P1(x)
        str_result += '\t'*5 + str(self.internal_nodes[1][0].branches[0])
        self.redis.set('p1x', str(self.internal_nodes[1][0].branches[0]))
        
        # P2(x)
        str_result += '\t'*3 + str(self.internal_nodes[1][0].branches[1])
        self.redis.set('p2x', str(self.internal_nodes[1][0].branches[1]))
        
        str_result += '\n'

        # Two Cards
        if self.amount == 2 or self.visited == False:
            str_result += (('\t'*5) if self.visited == False else ('\t'*5)) + str(self.internal_nodes[1][0].leaf_nodes[0])
            if self.visited:
                self.redis.set('cards_2_3', str(self.internal_nodes[1][0].leaf_nodes[0]))
        
        # Three Cards
        if self.amount == 3 or self.visited == False:
            str_result += (('\t'*3) if self.visited == False else ('\t'*9)) + str(self.internal_nodes[1][0].leaf_nodes[1])
            if self.visited:
                self.redis.set('cards_2_3', str(self.internal_nodes[1][0].leaf_nodes[1]))
        
        if self.amount == 0:
            if self.visited:
                self.redis.set('cards_2_3', '0')

                                                      
        return str_result
