from arrangements.StraightRoyalFlush import StraightRoyalFlush
from arrangements.Carriage import Carriage
from arrangements.Full import Full
from arrangements.Color import Color
from arrangements.Straight import Straight
from arrangements.ThreeOfAKind import ThreeOfAKind
from arrangements.TwoPairs import TwoPairs
from arrangements.OnePair import OnePair
from arrangements.HighCard import HighCard
from classes.DataFrameML import DataFrameML
import sys
import os

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__
    
class Arrangements(object):
    
    def __init__(self, cards = []):
        self.id_arr:int = 0
        self.data_frame_ml:DataFrameML = DataFrameML()
        self.cards:list = cards
        self.cards_after:list = []
        self.high_card:HighCard = HighCard()
        self.one_pair:OnePair = OnePair()
        self.two_pairs:TwoPairs = TwoPairs()
        self.three_of_a_kind:ThreeOfAKind = ThreeOfAKind()
        self.straight:Straight = Straight()
        self.color:Color = Color()
        self.full:Full = Full()
        self.carriage:Carriage = Carriage()
        self.straight_royal_flush:StraightRoyalFlush = StraightRoyalFlush() 
        
        self.arrangements:list = [self.high_card, self.one_pair, self.two_pairs, self.three_of_a_kind,
                          self.straight, self.color, self.full, self.carriage, self.straight_royal_flush] 
        
        self.rand_int:int = 0

    def set_cards(self, cards):   
        self.cards = cards             
        for x in self.arrangements:
            x.set_cards(self.cards)

    def set_weights(self):
        self.weights = []
        
        for x in self.arrangements:
            self.weights.append(x.get_weight())

        # Zwraca None, gdy niema potrzeby okreslania czesciowej wagi ukladu
        self.part_weights = []
        
        for x in self.arrangements:
            self.part_weights.append(x.get_part_weight())
                    
    def check_arrangement(self, game_visible=True):
        self.ids_arr = []
        if game_visible == False:
            blockPrint()
        
        for x in self.arrangements:
            x.set_rand_int(self.rand_int)
            self.ids_arr.append(x.arrangement_recogn()) 
        
        if game_visible == False:
            enablePrint()
        #print(self.ids_arr)

    def set_rand_int(self, rand_int):
        self.rand_int = rand_int
        
    def get_cards(self):
        return self.cards

    def get_data_frame_ml(self):
        return self.data_frame_ml

    def set_data_frame_ml(self, data_frame_ml: DataFrameML = None):
        self.data_frame_ml = data_frame_ml

    def init_data_frame_ml_before_ex(self):   
        self.data_frame_ml.id_arr = self.get_id()       
        self.data_frame_ml.weight = self.get_weight()       
        self.data_frame_ml.weight_ex = self.get_part_weight_sum(self.part_weights)    

    def init_data_frame_ml_after_ex(self):      
        #self.data_frame_ml.id_arr = self.get_id()  
        self.data_frame_ml.weight_after_ex = self.get_weight() 
        #[self.data_frame_ml.set_cards_after(self.get_part_weight()[idx]) for idx in range(0, len(self.get_part_weight()))]
        [self.data_frame_ml.set_cards_after(card.weight) for card in self.cards_after]

        self.data_frame_ml.weight_ex = self.get_part_weight_sum(self.part_weights)

    def set_cards_after(self, cards):
        self.cards_after = cards
    
    def get_weight(self):
        for weight in self.weights:
            if weight is not None:
                return weight
    
    def get_part_weight(self):
        for part_weight in self.part_weights:
            if part_weight is not None:
                #print(part_weight)
                return part_weight

    def get_part_weight_sum(self, part_cards):
        if not part_cards:
            return 0

        part_weight = part_cards.pop()
        
        if part_weight is None:
            return 0
        
        return part_weight + self.get_part_weight_sum(part_cards)

    def get_id(self):
        for id_arr in self.ids_arr:
            if id_arr is not None:
                return id_arr

    def print(self):
        for idx in self.cards:
            idx.print()