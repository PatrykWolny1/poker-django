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
from home.redis_buffer_singleton import redis_buffer_instance
import sys
import os

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__
    
class Arrangements(object):
    
    def __init__(self, cards = [], all_arrangements = True, unique_session_id = None):
        self.id_arr:int = 0
        self.ids_arr:list = []
        self.data_frame_ml:DataFrameML = DataFrameML()
        self.cards:list = cards
        self.cards_after:list = []
        
        which_arrangement = None

        if not all_arrangements:
            which_arrangement = redis_buffer_instance.redis_1.get(f'arrangement_{unique_session_id}').decode('utf-8')   
            print(which_arrangement)

        if which_arrangement == '9' or all_arrangements:
            self.high_card:HighCard = HighCard()
        if which_arrangement == '8' or all_arrangements:
            self.one_pair:OnePair = OnePair()
        if which_arrangement == '7' or all_arrangements:
            self.two_pairs:TwoPairs = TwoPairs()
        if which_arrangement == '6' or all_arrangements:
            self.three_of_a_kind:ThreeOfAKind = ThreeOfAKind()
        if which_arrangement == '5' or all_arrangements:
            self.straight:Straight = Straight()
        if which_arrangement == '4' or all_arrangements:
            self.color:Color = Color()
        if which_arrangement == '3' or all_arrangements:
            self.full:Full = Full()
        if which_arrangement == '2' or all_arrangements:
            self.carriage:Carriage = Carriage()
        if which_arrangement == '1' or all_arrangements:
            self.straight_royal_flush:StraightRoyalFlush = StraightRoyalFlush() 
        
        if all_arrangements:
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
                    
    def check_arrangement(self, game_visible=True, is_result=False):
        self.ids_arr = []
        
        arr_str = None
        
        if game_visible == False:
            blockPrint()
        
        for x in self.arrangements:
            x.set_rand_int(self.rand_int)
            self.ids_arr.append(x.arrangement_recogn()) 
            
            if not is_result:
                if isinstance(x, OnePair):
                    arr_str = "Jedna Para: " + str(x.weight_arrangement) + " Wysoka karta: " + x.high_card.print_str() + "\n"
            else:
                which_arr = x.arrangement_recogn()
                if which_arr == 1:
                    arr_str = "Wysoka Karta: " + str(x.weight_arrangement) + " Wysoka karta: " + x.high_card_1.print_str() + "\n"
                elif which_arr == 2:
                    arr_str = "Jedna Para: " + str(x.weight_arrangement) + " Wysoka karta: " + x.high_card.print_str() + "\n"
                elif which_arr == 3:
                    arr_str = "Dwie pary: " + str(x.two_pairs_sum) + " Wysoka Karta: " + x.high_card.print_str() + "\n"
                elif which_arr == 4:
                    arr_str = "Trojka: " + str(x.weight_arrangement) + " Wysoka Karta: " + x.high_card.print_str() + "\n"
                elif which_arr == 5:
                    arr_str = "Strit: " + str(x.weight_arrangement) + "\n"
                elif which_arr == 6:
                    arr_str = "Kolor: " + str(x.color_sum) + " Wysoka Karta: " + x.high_card.print_str() + "\n"
                elif which_arr == 7:
                    arr_str = "Full: " + str(x.weight_arrangement) + "\n"
                elif which_arr == 8:
                    arr_str = "Kareta: " + str(x.weight_arrangement) + "\n"
                elif which_arr == 9:
                    arr_str = "Poker: " + str(x.weight_arrangement) + "\n"
                elif which_arr == 10:
                    arr_str = "Poker Krolewski: " + str(x.weight_arrangement) + "\n"
    
        if game_visible == False:
            enablePrint()
        #print(self.ids_arr)
        
        return arr_str

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