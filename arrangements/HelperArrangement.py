import random
from itertools import chain
import pickle
import time
import shutil
import os
from pathlib import Path
from home.redis_buffer_singleton import redis_buffer_instance, redis_buffer_instance_stop
from home.ThreadVarManagerSingleton import task_manager

class HelperArrangement(object):
    indices_2d:list = []                     #Indeksy ukladow kart figury
    indices_2d_color:list = []               # kolory
    cards_all_permutations:list = []         #Tablica na permutacje - losowy uklad
    weight_gen:list = []                     #Tablica na wagi kart
    perm:list = []

    rand_int:int = 0
    
    def __init__(self, helper_file_class):
        self.helper_file_class = helper_file_class
        self.cards_all_permutations.clear()
    
    def dim(self, a):
        #Jesli to nie jest lista to zwroc pusty zbior
        if not type(a) == list:
            return []
        #Rekurencja. Dodawanie kolejno dlugosci kolejnych tablic np. [1 5 10 15] czyli 4-wymiarowa
        return [len(a)] + self.dim(a[0])

    def get_indices_1(self, cards):        
        size = len(cards)

        # Sprawdzanie oraz zapisanie indeksow powtarzajacych sie kart
        if self.dim(cards) == 2:
            cards = [item for sublist in cards for item in sublist]
            #print(cards)
        if self.dim(cards) == 1:
            cards = [cards]
        
        for idx in range(0, size):
            indices = []
            for (index, card) in enumerate(cards):
                if card.name == cards[idx].name:
                    indices.append(index)
            self.indices_2d.append(indices)
        # print(self.indices_2d)
        return self.indices_2d

    def get_indices_color(self, cards, random = False, example = False):
        # if random == True and example == True:
        #     for idx in range(0, len(cards)):
        #         indices = []
        #         for (index, card) in enumerate(cards):
        #             if card.color == cards[idx].color:
        #                 indices.append(index)
        #         self.indices_2d_color.append(indices)
        #     #print(self.indices_2d_color)
        #     return

        # if self.dim(cards) == 1:
        cards = [cards]

        # Sprawdzanie oraz zapisanie indeksow powtarzajacych sie kart
        for idx in range(0, len(cards)):
            for idx1 in range(0, len(cards[idx])):
                indices = []
                for (index, card) in enumerate(cards[idx]):
                    if card.color == cards[idx][idx1].color:
                        indices.append(index)
                self.indices_2d_color.append(indices)
        #print(self.indices_2d_color)

    def check_if_weights_larger(self, show = False):
        # Sprawdzanie czy wagi w wygenerowanych ukladach sa wieksze niz poprzedni uklad (min -> max)
        self.weight_gen = [ele for ele in self.weight_gen if ele != []]
        indices = []
        # print("Wagi: ")
        count_all_weights = 0
        idx1 = 1

        for idx2 in range(0, len(self.weight_gen)):
            if (idx1 == len(self.weight_gen)):
                # print("Dlugosc tablicy: ", len(self.weight_gen))
                # print("Wszystkie liczby sprawdzone: ", count_all_weights)
                break
            if (self.weight_gen[idx2] <= self.weight_gen[idx1]):
                # print(self.weight_gen[idx2], "[", idx2, "]", "<=", self.weight_gen[idx1], "[", idx1, "]")
                count_all_weights += 1
            elif (self.weight_gen[idx2] > self.weight_gen[idx1]):
                # Dodawanie indeksow permutacji ktore nie pasuja (poprzednia wieksza od nastepnej)
                indices.append(idx2)
                indices.append(idx1)
            idx1 += 1

        if show == True:
            # Wyswietlenie ukladow ktore nie pasuja
            for idx in range(0, len(indices)):
                for idx1 in range(0, len(self.cards_all_permutations[indices[idx]])):
                    # print(self.cards_all_permutations[indices[idx]][idx1].print_str(), end=" ")
                    if idx1 == 4:
                        pass
                        # print(indices[idx])
                # print()

    def random_arrangement(self, if_combs=True):
        #Zerowanie pustych wierszy
        self.cards_all_permutations = [ele for ele in self.cards_all_permutations if ele != []]
        
        self.rand_int = random.sample(range(0, len(self.weight_gen) - 1), 2)
        cards = None
        try:
        #if if_combs == True:
            cards = [self.cards_all_permutations[self.rand_int[0]],  
                    self.cards_all_permutations[self.rand_int[1]]]
        except IndexError:
            print("INDEX ERROR: ", self.rand_int[0], self.rand_int[1], len(self.weight_gen), len(self.cards_all_permutations))
        
        #else:
         #   cards = self.cards_all_permutations[self.rand_int[0]]
        
        # idx1 = 0
        # idx2 = 0
        
        # iter_idx = 0
        # if_not_the_same = True
        # repeat = 0
        
        # while(if_not_the_same and if_combs):
        #     idx1 = 0

        #     while idx1 < len(cards[0]):
        #         idx2 = 0
        #         repeat = 0
        #         while idx2 < len(cards[1]):
        #             if cards[0][idx1] == cards[1][idx2]:
        #                 repeat += 1
        #                 cards[1] = []
        #                 #print(len(self.weight_gen))
        #                 #print(len(self.cards_all_permutations))
        #                 cards[1] = self.cards_all_permutations[random.sample(range(0, len(self.weight_gen) - 1), 1)[0]]
                        
        #                 iter_idx=0
        #                 idx1 = 0
        #                 break
                    
        #             if iter_idx == 19 and repeat == 0:
        #                 if_not_the_same = False
        #             iter_idx += 1
        #             idx2 += 1
        #         if repeat == 0:
        #             idx1 += 1 
                        
        #         iter_idx += 1   
                            
        # print("Wylosowany uklad: ", self.rand_int)
        with task_manager.cache_lock_event_var:
            redis_buffer_instance.redis_1.set('count_arrangements', "Ilosc ukladow (CALOSC): " + str(len(self.cards_all_permutations)))

        try:
            shutil.copyfile(self.helper_file_class.file_path.resolve(), self.helper_file_class.file_path_dst.resolve())
        except Exception as e:
            print(f"Error copying file: {e}")
        
        redis_buffer_instance.redis_1.set('prog_when_fast', '100')

        redis_buffer_instance_stop.redis_1.set('stop_event_var', '1')     

      
        
        when_game_one_pair = redis_buffer_instance.redis_1.get('when_one_pair').decode('utf-8')
        
        print("IN HELPER when_game_one_pair", when_game_one_pair)
        
        if when_game_one_pair == '0':
            HelperArrangement.weight_gen.clear()
            HelperArrangement.cards_all_permutations.clear()

        return cards, self.rand_int, self.cards_all_permutations
        
    def get_indices_2d_1(self):
        return self.indices_2d

    def get_indices_2d_color(self):
        return self.indices_2d_color

    def get_cards_all_permutations(self):
        return self.cards_all_permutations

    def get_rand_int(self):
        return self.rand_int
    
    def append_cards_all_permutations(self, cards_perm):
        self.cards_all_permutations.append(cards_perm)

    def append_weight_gen(self, weight_arrangement):
        self.weight_gen.append(weight_arrangement)

    def clear_indices_2d_1(self):
        self.indices_2d.clear()

    def clear_indices_2d_color(self):
        self.indices_2d_color.clear()

