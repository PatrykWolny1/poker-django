from classes.Arrangements import Arrangements
from classes.Deck import Deck
from classes.Card import Card
from random import choice
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_one_pair_game
from home.ThreadVarManagerSingleton import task_manager
import sys
import os

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

class Player(object):
    it_cards:int = 0
    cards_2d:list = []
   
    def __init__(self, deck = Deck(), nick = "Nick", index = None, perm = None, if_deck = None, 
                 cards = [], if_show_perm = None, si_boolean = None):
        deck.shuffling()
        self.cards_exchanged:list = []
        self.nick:str = nick
        self.arrangements:Arrangements = Arrangements()
        self.cards:list = []
        self.all_comb_perm:list = []
        self.si_boolean:bool = si_boolean
        self.index:int = index
        
        if if_deck == True and if_show_perm == False:

            for idx in range(5):
                self.cards.append(deck.deal())

            self.arrangements.set_cards(self.cards)
        elif if_show_perm == False and perm == False:
            self.cards = cards
            deck.pop_from_deck(self.cards)
            self.arrangements.set_cards(self.cards)
        elif if_show_perm == False and perm == True:
            #deck.print()
            self.cards = cards
            self.arrangements.set_cards(self.cards)
            #self.print()
            deck.pop_from_deck(self.cards)
            #deck.print()
        
        
    def return_to_croupier(self, amount = 0, cards_to_exchange = [], game_visible = True, si_boolean = None):
        self.amount = amount
        temp = self.cards.copy()

        if self.amount == 0:
            return self.amount

        for idx in range(0, self.amount):
            if idx == 0:
                if game_visible == True:
                    self.print()

            if self.amount != 5:
                if si_boolean == True:
                    which_card = choice(list(range(1, len(self.cards) + 1)))            
                    
                    if game_visible == True:
                        print()
                    
                    if amount == 2 and si_boolean == True:
                    #which_card = self.cards.index(cards_to_exchange[idx]) + 1
                        
                        which_card_card = next((card for card in self.cards if card.weight == cards_to_exchange[idx]), None)
                        which_card = self.cards.index(which_card_card) + 1     
                        which = int(which_card)
                        temp_card = temp.pop(which - 1)
                        self.cards_exchanged.append(temp_card)
                        
                    if amount == 3 and si_boolean == True:
                        #which_card = self.cards.index(cards_to_exchange[idx]) + 1
                        
                        which_card_card = next((card for card in self.cards if card.weight == cards_to_exchange[idx]), None)
                        which_card = self.cards.index(which_card_card) + 1
                        which = int(which_card)
                        temp_card = temp.pop(which - 1)
                        self.cards_exchanged.append(temp_card)
                    
                    if game_visible == True:    
                        print("Ktora karta: ", which_card)

                        print()
                    
                    if amount == 2 and idx == 1 and si_boolean == True:
                        self.cards_exchanged.append(Card(empty=True))
                else:
                    self.print()
                    which_card = input("Ktora karta[1-5]: ")
                    which = int(which_card)
                    temp_card = temp.pop(which - 1)
                    self.cards_exchanged.append(temp_card)
                
            else:
                temp.pop()

            self.cards = temp
            if game_visible == True:    
                self.print()

        if self.amount == 5:
            self.arrangements.set_cards(self.cards)
        
        if game_visible == True:    
            print()

        return self.amount

    def take_cards(self, deck):
        self.cards.append(deck.deal())
        self.arrangements.set_cards_after(self.cards)

    def cards_permutations(self, rand_arr = False, combs_gen = False, queue = None):
            if combs_gen == False:
                # print("Wybierz rodzaj permutacji (1 - ALL | 2 - RANDOM | 3 - WYJSCIE: ")
                if_rand = '1'    #if_rand == '2' if generate random with permutations (too many...)
                if_combs = False
            else:
                if_rand = "1"
                if_combs = True
                
            
            if if_rand == "1":
                self.random = False
            elif if_rand == "2":
                self.random = True
                rand_arr = True
            elif if_rand == "3":
                return 0

            # print(f"Wybierz uklad do wygenerowania:\n"
            #     "(1 - POKER/POKER KROLEWSKI)\n"
            #     "(2 - KARETA)\n"
            #     "(3 - FULL)\n"
            #     "(4 - KOLOR)\n"
            #     "(5 - STRIT)\n"
            #     "(6 - TROJKA\n"
            #     "(7 - DWIE PARY)\n"
            #     "(8 - JEDNA PARA)\n"
            #     "(9 - WYSOKA KARTA)\n", flush=True)

            # arrangement = input()
            arrangement = None
            choice = redis_buffer_instance.redis_1.get('choice').decode('utf-8')
            if choice == '1':
                arrangement = redis_buffer_instance.redis_1.get('arrangement').decode('utf-8')  # Binary code for Carriage
                if redis_buffer_instance.redis_1.get('straight_royal_flush') is not None:
                    straight_royal_flush = redis_buffer_instance.redis_1.get('straight_royal_flush').decode('utf-8')
                else:
                    straight_royal_flush = '-1'
                if straight_royal_flush == '0':
                    straight_royal_flush = False
                elif straight_royal_flush == '1':
                    straight_royal_flush = True
            if choice == '2':
                arrangement = '8'
                    
            # Gra jednym ukladem kart
            with task_manager.cache_lock_event_var:
                if combs_gen == True:
                    redis_buffer_instance.redis_1.set('print_gen_combs_perms', "Generowanie kombinacji kart...")
                    # print("Generowanie kombinacji kart...")
                else:
                    redis_buffer_instance.redis_1.set('print_gen_combs_perms', "Generowanie permutacji kart...")
                    # print("Generowanie permutacji kart...")
            #blockPrint()
            
            redis_buffer_instance_one_pair_game.redis_1.set('thread_status', 'ready')

            if arrangement == "1":
                self.cards, self.rand_int, self.all_comb_perm = self.arrangements.straight_royal_flush.straight_royal_flush_generating(self.random, if_combs, straight_royal_flush)
            if arrangement == "2":
                self.cards, self.rand_int, self.all_comb_perm = self.arrangements.carriage.carriage_generating(self.random, if_combs)
            if arrangement == "3":
                self.cards, self.rand_int, self.all_comb_perm = self.arrangements.full.full_generating(self.random, if_combs)
            if arrangement == "4":
                self.cards, self.rand_int, self.all_comb_perm = self.arrangements.color.color_generating(self.random, if_combs)
            if arrangement == "5":
                self.cards, self.rand_int, self.all_comb_perm = self.arrangements.straight.straight_generating(self.random, if_combs)
            if arrangement == "6":
                self.cards, self.rand_int, self.all_comb_perm = self.arrangements.three_of_a_kind.three_of_a_kind_generating(self.random, if_combs)
            if arrangement == "7":
                self.cards, self.rand_int, self.all_comb_perm = self.arrangements.two_pairs.two_pairs_generating(self.random, if_combs)
            if arrangement == "8":
                self.cards, self.rand_int, self.all_comb_perm = self.arrangements.one_pair.one_pair_generating(self.random, if_combs)
            if arrangement == "9":
                self.cards, self.rand_int, self.all_comb_perm = self.arrangements.high_card.high_card_generating(self.random, if_combs)
            
            when_game_one_pair = redis_buffer_instance.redis_1.get('when_one_pair').decode('utf-8')

            if queue is not None and when_game_one_pair == '1':
                print("One pair game or not: ", when_game_one_pair)
                queue.put(self.all_comb_perm)
            
            #print(self.cards)
            
            self.cards = list(self.cards)
            
            if rand_arr:
                self.arrangements.set_cards(list(self.cards[0]))
                self.arrangements.set_rand_int(self.rand_int)
                self.arrangements.print()
                self.arrangements.check_arrangement()
            
            #enablePrint()
            if choice == '1':
                return self.cards, self.rand_int, self.all_comb_perm
            if choice == '2':
                return 0
            return self.cards, self.rand_int, self.all_comb_perm

                
    def get_arrangements(self):
        return self.arrangements

    def get_weight(self):
        return self.weight

    def get_cards(self):
        return self.cards
    
    def get_rand_int(self):
        return self.rand_int

    def set_cards(self, cards):
        self.cards = cards

    def set_win_or_not(self, win_or_not):
        self.win_or_not = win_or_not

    def print(self, all_part = False):
        print(self.nick)
        
        if all_part == False:
            for idx in self.cards:
                idx.print()
            print()
        else:
            for idx in self.cards_exchanged:
                idx.print()
            print()
    
