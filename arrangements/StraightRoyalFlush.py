from classes.Card import Card
from arrangements.HelperArrangement import HelperArrangement
from arrangements.HelperFileClass import HelperFileClass
from arrangements.LoadingBar import LoadingBar
from arrangements.CardMarkings import CardMarkings
from home.redis_buffer_singleton import redis_buffer_instance
from itertools import permutations
from pathlib import Path
import sys
import time

class StraightRoyalFlush(HelperArrangement):
    
    def __init__(self):
        self.cardmarkings:CardMarkings = CardMarkings()  #Oznaczenia kart
        self.file_path = Path("permutations_data/straight_royal_flush.txt")   
        self.file = open(self.file_path.resolve(), "w")
        self.helper_file_class = HelperFileClass(self.file_path.resolve())
        self.helper_arr = HelperArrangement(self.helper_file_class)
        
        self.max_value_generate:int = int(redis_buffer_instance.redis_1.get("entered_value").decode('utf-8'))
        if self.max_value_generate < 100:
            n_loading_bar = 1
        else:
            n_loading_bar = 100

        self.loading_bar:LoadingBar = LoadingBar('straightroyalflush', self.max_value_generate, n_loading_bar, n_loading_bar, self.helper_arr)
        self.loading_bar_combs:LoadingBar = LoadingBar('straightroyalflush_combs', self.max_value_generate, n_loading_bar, n_loading_bar, self.helper_arr)
        
        self.max_combs:str = str(int(self.loading_bar_combs.total_steps/self.loading_bar_combs.display_interval))
        self.max_1:str = str(int(self.loading_bar.total_steps/self.loading_bar.display_interval))  
                
        self.cards:list = []                     #Tablica na karty
        self.perm:list = []                      #Tablica na permutacje do wag
        self.temp:list = []

        self.weight_arrangement:int = 0         #Tablica na wage ukladu
        self.num_arr:int = 0                    #Liczenie ukladow kart w kolejnych iteracjach
        self.c_idx2:int = 0
        self.rand_int:int = 0
        self.step1:int = 0
        self.step2:int = 0

        self.random:bool = False                 #Jesli jest losowanie ukladu
        self.example:bool = False                #Jesli jest recznie wpisany uklad
        self.if_royal_flush:bool = False         #Jesli jest poker krolewski (prawda) lub poker (falsz)
        self.calc_weights:bool = True            #Zakonczenie petli while oraz identyfikacja czy jest to poker lub poker krolewski
        self.if_combs:bool = False
        self.stop:bool = True
        self.straight_royal_flush = True
        
    def set_cards(self, cards):
        self.perm = cards
        self.example = True
        self.random = True
    
    def set_rand_int(self, rand_int):
        self.rand_int = rand_int
        
    def get_weight(self):
        if self.weight_arrangement > 0:
            return self.weight_arrangement

    def get_part_weight(self):
        return 0

    def print_arrengement(self):
        if self.random == False and self.if_royal_flush == False:
            print("Poker: ", self.weight_arrangement, " Numer: ", self.num_arr)
        elif self.random == True and self.if_royal_flush == False:
           print("Poker: ", self.weight_arrangement, " Numer: ", self.rand_int)
        elif self.random == False and self.if_royal_flush == True:
            print("Poker Krolewski: ", self.weight_arrangement, "Numer: ", self.num_arr)
        elif self.random == True and self.if_royal_flush == True:
            print("Poker Krolewski: ", self.weight_arrangement, "Numer: ", self.rand_int)

    def straight_royal_flush_recognition(self, cards):
        #Czy jest 5 takich samych kolorow
        
        self.helper_arr.clear_indices_2d_color()
                
        self.helper_arr.get_indices_color(cards)

        color_5 = False
        for idx in range(0, len(self.helper_arr.get_indices_2d_color())):
            if len(self.helper_arr.get_indices_2d_color()[idx]) == 5:
                color_5 = True

        #Czy 5 wag zostalo sprawdzonych
        weight_5 = 0
        for idx2 in range(0, len(cards)):
            # Sprawdzanie wag dla kart o wagach od 9 do 13 (Poker Krolewski) 10...A
            if cards[idx2].weight in [9, 10, 11, 12, 13]:
                weight_5 += 1
            # Prawda dla Pokera Krolewskiego
            if color_5 == True and idx2 == 4 and weight_5 == 5:
                return True

        return False

    def arrangement_recognition_weights(self):
        if self.if_combs:
            self.perm = self.temp[self.c_idx2][self.step1:self.step2]
            
        ace_five = False
        
        if len(self.helper_arr.dim(self.perm)) == 1:
            self.perm = [self.perm]
            self.c_idx2 = 0
            
        if sorted(self.perm[self.c_idx2])[4].weight == 13 and sorted(self.perm[self.c_idx2])[3].weight == 4:
            ace_five = True 
            
        #Rozpoznawanie ukladu oraz obliczanie wagi
        weight_iter = 0
        straight_weight = 0
        self.calc_weights = True
        idx1 = 0
        idx2 = 1
        
        self.helper_arr.clear_indices_2d_1()
        self.helper_arr.clear_indices_2d_color()
        
        self.helper_arr.get_indices_color(self.perm[self.c_idx2])
        self.helper_arr.get_indices_1(self.perm[self.c_idx2])
        
        while (self.calc_weights):
            
            # Dla posortowanej tablicy sprawdz czy waga jest mniejsza od kolejnej
            for idx in range(0, len(self.helper_arr.get_indices_2d_1())):
                # Jesli jest 5 takich samych kolorow to powrot z funkcji (poker krolewski)
                if len(self.helper_arr.get_indices_2d_1()[idx]) > 1:
                    return
                if len(self.helper_arr.get_indices_2d_color()[idx]) != 5:
                    return

            if idx1 == 4:
                break
            
            # Jesli waga pierwszej karty jest mniejsza od drugiej ... do 5 karty to jest to strit
            if ((sorted(self.perm[self.c_idx2])[idx2].weight - sorted(self.perm[self.c_idx2])[idx1].weight == 1) or
                    (sorted(self.perm[self.c_idx2])[4].weight == 13 and ((sorted(self.perm[self.c_idx2])[4].weight - sorted(self.perm[self.c_idx2])[3].weight) == 9))):

                if ace_five == True:
                    #print(idx1 + 2, sorted(self.perm[self.c_idx2])[idx1].print_str())
                    straight_weight += sorted(self.perm[self.c_idx2])[idx1].weight
                    weight_iter += 1

                    if sorted(self.perm[self.c_idx2])[idx2].weight == 13:
                        #print("1", sorted(self.perm[self.c_idx2])[idx2].print_str())
                        straight_weight += sorted(self.perm[self.c_idx2])[idx2].weight - 20
                        weight_iter += 1
                else:
                    #print(idx1 + 1, sorted(self.perm[self.c_idx6])[idx1].print_str())
                    straight_weight += sorted(self.perm[self.c_idx2])[idx1].weight
                    weight_iter += 1
                    #print(straight_weight)

                    if idx2 == 4:
                        #print(idx2 + 1, sorted(self.perm[self.c_idx6])[idx2].print_str())
                        straight_weight += sorted(self.perm[self.c_idx2])[idx2].weight
                        weight_iter += 1
                        #print(straight_weight)

                # Jesli jest strit to weight_iter == 4. Liczono od 0
                if weight_iter == 5:
                    self.weight_arrangement = straight_weight + 12448474
                    self.helper_arr.append_weight_gen(self.weight_arrangement)

                    self.if_royal_flush = self.straight_royal_flush_recognition(sorted(self.perm[self.c_idx2]))

                    if self.random == False:
                        #self.print_arrengement()

                        if self.if_royal_flush == False:
                            self.file.write("Poker: " + str(self.weight_arrangement) + " Numer: " + str(self.num_arr) + "\n")
                        else:
                            self.file.write("Poker Krolewski: " + str(self.weight_arrangement) + " Numer: " + str(self.num_arr) + "\n")
                                               
                
                    if self.example == True:
                        self.print_arrengement()
                
                        for idx in range(0, len(self.perm[self.c_idx2])):
                            with open("permutations_data/straight_royal_flush.txt", 'a') as file:
                                file.write(self.perm[self.c_idx2][idx].print_str() + " ")
                        with open("permutations_data/straight_royal_flush.txt", 'a') as file:
                            file.write("\n")
                                        
                        if self.if_royal_flush == False:
                            with open("permutations_data/straight_royal_flush.txt", 'a') as file:
                                file.write("Poker: " + str(self.weight_arrangement) + " Numer: " + str(self.rand_int) + "\n")
                        else:
                            with open("permutations_data/straight_royal_flush.txt", 'a') as file:
                                file.write("Poker Krolewski: " + str(self.weight_arrangement) + " Numer: " + str(self.rand_int) + "\n")

                    self.num_arr += 1
         
                    self.calc_weights = False

            idx1 += 1
            idx2 += 1

    def arrangement_recogn(self):
        self.arrangement_recognition_weights()

        if self.example == True:
            if self.if_royal_flush == True and self.calc_weights == False:
                return 10
            elif self.if_royal_flush == False and self.calc_weights == False:
                return 9

    def straight_royal_flush_generating(self, random, if_combs, straight_royal_flush, session_id):
        self.random = random
        
        self.straight_royal_flush = straight_royal_flush
        
        self.if_combs = if_combs
        
        self.helper_arr.set_session_id(session_id)
        self.loading_bar.set_session_id(session_id)
        self.loading_bar_combs.set_session_id(session_id)
        self.helper_file_class.set_session_id(session_id)

        if self.if_combs:     
            redis_buffer_instance.redis_1.set(f'min_{session_id}', '0')
            redis_buffer_instance.redis_1.set(f'max_{session_id}', self.max_combs)
        else:
            redis_buffer_instance.redis_1.set(f'min_{session_id}', '0')
            redis_buffer_instance.redis_1.set(f'max_{session_id}', self.max_1)
        
        cards_2d = []
        m = 0
        for iter in range(0, 10):
            cards_1d = []
            if iter > 1:
                m += 1
            for color in self.cardmarkings.colors:
                for idx1, idx2 in zip(range(0, len(self.cardmarkings.arrangements)), range(0, 5)):
                    if iter == 0:
                        if idx1 == 0:
                            cards_1d.append(
                                Card(self.cardmarkings.arrangements[len(self.cardmarkings.arrangements) - 1],
                                     color))
                        if idx1 < 4:
                            cards_1d.append(Card(self.cardmarkings.arrangements[idx1], color))
                    else:
                        cards_1d.append(Card(self.cardmarkings.arrangements[idx1 + m], color))

                if color == 'Ka':
                    cards_2d.append(cards_1d[:])

        return self.check_generate_cards(cards_2d)

    def check_generate_cards(self, cards_2d):
        #Generowanie 5 kart oraz sprawdzanie jaki to uklad

        # for idx3 in range(0, len(cards_2d)):
        #     for idx4 in range(0, len(cards_2d[idx3])):
        #         cards_2d[idx3][idx4].print()
        #     print()

        #Konwertowanie tablicy kart do tymczasowej dwuwymiarowej tablicy
        for idx1 in range(0, len(cards_2d)):
            self.temp = []
            for idx2 in range(0, len(cards_2d[idx1])):
                self.cards.append(cards_2d[idx1][idx2])
            self.temp.append(self.cards)

        # for idx1 in range(0, len(self.temp)):
        #     for idx2 in range(0, len(self.temp[idx1])):
        #         self.temp[idx1][idx2].print()
        #     print()

        #Konwertowanie tymczasowej tablicy do tablicy na permutacje
        for idx1 in range(0, len(self.temp)):
            for self.step1, self.step2 in zip(range(0, len(self.temp[idx1]), 5), range(5, len(self.temp[idx1]) + 1, 5)):
                if self.if_combs:
                    self.if_royal_flush = self.straight_royal_flush_recognition(sorted(self.temp[idx1][self.step1:self.step2]))  
                    if self.if_royal_flush and self.straight_royal_flush:
                        for idx11 in range(0, len(self.temp[idx1][self.step1:self.step2])):
                            self.file.write(self.temp[idx1][self.step1:self.step2][idx11].print_str() + " ")
                                #print()
                        self.file.write("\n")
                        self.file.flush()

                        self.c_idx2 = idx1
                        self.arrangement_recogn()
                        self.helper_arr.append_cards_all_permutations(self.temp[idx1][self.step1:self.step2])

                        if not self.loading_bar_combs.update_progress(self.num_arr):
                                self.helper_arr.check_if_weights_larger(False)
                                self.file.close()
                                return self.helper_arr.random_arrangement()
                        
                        if not self.loading_bar_combs.check_stop_event():
                                sys.exit() 

                    
                    if not self.if_royal_flush and not self.straight_royal_flush:
                        for idx11 in range(0, len(self.temp[idx1][self.step1:self.step2])):
                            self.file.write(self.temp[idx1][self.step1:self.step2][idx11].print_str() + " ")
                                #print()
                        self.file.write("\n")
                        self.file.flush()
                        
                        self.c_idx2 = idx1
                        self.arrangement_recogn()
                        self.helper_arr.append_cards_all_permutations(self.temp[idx1][self.step1:self.step2])
                        
                        if not self.loading_bar_combs.update_progress(self.num_arr):
                                self.helper_arr.check_if_weights_larger(False)
                                self.file.close()
                                return self.helper_arr.random_arrangement()
                        
                        if not self.loading_bar_combs.check_stop_event():
                                sys.exit() 


                if not self.if_combs:               
                        #Generowanie tablicy permutacji   
                        self.perm = list(permutations(self.temp[idx1][self.step1:self.step2]))

                        self.perm = [list(i) for i in self.perm]
                    
                        for idx2 in range(0, len(self.perm)):
                            self.if_royal_flush = self.straight_royal_flush_recognition(sorted(self.perm[idx2]))
                            if self.if_royal_flush and self.straight_royal_flush:    
                                if self.random == False:
                                    for idx3 in range(0, len(self.perm[idx2])):
                                        #self.perm[idx2][idx3].print()
                                        self.file.write(self.perm[idx2][idx3].print_str() + " ")
                                    #print()
                                    self.file.write("\n")
                                    self.file.flush()
                                    
                                    self.c_idx2 = idx2
                                    self.arrangement_recogn()
                                    self.helper_arr.append_cards_all_permutations(self.perm[idx2])
                            
                                    if not self.loading_bar.update_progress(self.num_arr):
                                        self.helper_arr.check_if_weights_larger(False)
                                        self.file.close()
                                        return self.helper_arr.random_arrangement()
                                    
                                    if not self.loading_bar.check_stop_event():
                                        sys.exit()   
                                        

                                
                            if not self.if_royal_flush and not self.straight_royal_flush:
                                if self.random == False:
                                    for idx3 in range(0, len(self.perm[idx2])):
                                        #self.perm[idx2][idx3].print()
                                        self.file.write(self.perm[idx2][idx3].print_str() + " ")
                                    #print()
                                    self.file.write("\n")
                                    self.file.flush()

                                    self.c_idx2 = idx2
                                    self.arrangement_recogn()     
                                    self.helper_arr.append_cards_all_permutations(self.perm[idx2])
                            
                                    if not self.loading_bar.update_progress(self.num_arr):
                                            self.helper_arr.check_if_weights_larger(False)
                                            self.file.close()
                                            return self.helper_arr.random_arrangement()
                                    
                                    if not self.loading_bar.check_stop_event():
                                        sys.exit()   
                                        

                    
        self.helper_arr.check_if_weights_larger()

        self.file.close()

        return self.helper_arr.random_arrangement()