from arrangements.HelperArrangement import HelperArrangement
from arrangements.LoadingBar import LoadingBar
from arrangements.CardMarkings import CardMarkings
from arrangements.HelperFileClass import HelperFileClass
from pathlib import Path
from classes.Card import Card
from itertools import permutations, combinations
from home.redis_buffer_singleton import redis_buffer_instance
import sys

class HighCard(HelperArrangement):

    def __init__(self):
        self.cardmarkings:CardMarkings = CardMarkings()   # Oznaczenia kart
        self.high_card_1:Card = Card()
        self.limit_rand:int = 100000            # Liczba kombinacji kart -> pomnozone przez 120 daje liczbe permutacji
        self.one_iter:int = 120    
        
        self.file_path = Path("permutations_data/high_card.txt")   
        self.file = open(self.file_path.resolve(), "w")
        self.helper_file_class = HelperFileClass(self.file_path.resolve())
        self.helper_arr = HelperArrangement(self.helper_file_class)
        self.max_value_generate:int = int(redis_buffer_instance.redis_1.get("entered_value").decode('utf-8'))

        self.loading_bar:LoadingBar = LoadingBar('highcard', self.max_value_generate, 100, 100, self.helper_arr)   # 156 304 800 permutacji           
        self.loading_bar_combs:LoadingBar = LoadingBar('highcard_combs', self.max_value_generate, 100, 100, self.helper_arr)   # 1 302 540 kombinacji           
        
        self.max_combs:str = str(int(self.loading_bar_combs.total_steps/self.loading_bar_combs.display_interval))
        self.max_1:str = str(int(self.loading_bar.total_steps/self.loading_bar.display_interval))
        
        self.perm:list = []                       # Lista na karty gracza
        self.weight_arrangement_part:list = []    # Lista na wagi wszystkich kart
        self.cards_comb_rest:list = []
        
        self.high_card_weight:int = 0            # Waga najwyzszej karty
        self.idx_bar:int = 0
        self.weight_arrangement:int = 0          # Waga ukladu
        self.c_idx1:int = 0                      # Zapisywanie aktualnego indeksu z petli for
        self.num_arr:int = 0                     # Numer ukladu
        self.iter_rand:int = 0                   # Ilosc wykonanych iteracji dla tworzenia permutacji ukladow
        self.num_arr_combs:int = 0
        
        self.random:bool = False
        self.example:bool = False
        self.if_combs:bool = False
        self.stop:bool = True
    
    def set_cards(self, cards):
        self.perm = cards
        self.example = True
        self.random = True

    def set_rand_int(self, rand_int):
        self.rand_int = rand_int
        
    def get_weight(self):
        # Jesli nie wystepuje uklad to waga wynosi 0
        if self.weight_arrangement > 0:
            return self.weight_arrangement

    def get_part_weight(self):
        if sum(self.weight_arrangement_part) > 0:
            return self.weight_arrangement_part

    def print_arrengement(self):
        if self.random == False:
            print("Wysoka karta: ", self.weight_arrangement, "Wysoka karta: ", self.high_card_1.print_str(),  "Numer: ", self.num_arr)
        if self.random == True:
            print("Wysoka karta: ", self.weight_arrangement, "Wysoka karta: ", self.high_card_1.print_str(),  "Numer: ", self.rand_int)

    def card_max(self, perm_temp, pow_idx):
        # Jesli lista jest pusta to wyjdz
        if not perm_temp:
            return 0

        # Wybor maksymalnej wartosci z ukladu
        card_temp = max(perm_temp)

        self.weight_arrangement_part.append(card_temp.weight)

        # Obliczenie wagi a nastepnie usuniecie kart z listy w celu pobrania nastepnej maksymalnej wartosci
        self.high_card_weight = pow(card_temp.weight, pow_idx)

        perm_temp.remove(card_temp)

        pow_idx -= 1

        # Rekurencja (Dodanie poprzedniej wagi do nastepnej)
        return self.high_card_weight + self.card_max(perm_temp, pow_idx)

    def arrangement_recogn(self):
        if self.example == True:
            self.c_idx1 = 0
            
            if len(self.helper_arr.dim(self.perm)) == 1:
                self.perm = [self.perm]

        straight_iter = 0
        self.weight_arrangement_part = []
        
        if self.if_combs:
            self.perm = self.cards_comb_rest
            

        # Jesli uklad to strit to powrot z funkcji
        for idx2, idx1 in zip(range(1, len(self.perm[self.c_idx1])), range(0, len(self.perm[self.c_idx1]))):
            if ((sorted(self.perm[self.c_idx1])[idx2].weight - sorted(self.perm[self.c_idx1])[idx1].weight == 1) or
             (sorted(self.perm[self.c_idx1])[4].weight == 13 and (sorted(self.perm[self.c_idx1])[4].weight - sorted(self.perm[self.c_idx1])[3].weight) == 9)):
                straight_iter += 1

            if straight_iter == 4:
                self.weight_arrangement_part = [0]
                return
        
        self.helper_arr.clear_indices_2d_1()        
        self.helper_arr.clear_indices_2d_color()
        
        self.helper_arr.get_indices_1(self.perm[self.c_idx1])
        self.helper_arr.get_indices_color(self.perm[self.c_idx1])

        # Jesli uklad to kolor lub jest wiecej takich samych figure niz 1 to powrot z funkcji
        for idx3, idx4 in zip(range(0, len(self.helper_arr.get_indices_2d_color())), range(0, len(self.helper_arr.get_indices_2d_1()))):
            # Jesli jest 5 takich samych kolorow to powrot z funkcji (poker krolewski)
            if len(self.helper_arr.get_indices_2d_color()[idx3]) == 5:
                self.weight_arrangement_part = [0]
                return
            if len(self.helper_arr.get_indices_2d_1()[idx4]) > 1:
                self.weight_arrangement_part = [0]
                return

        # Najwieksza karta dla jej wyswietlenia
        self.high_card_1 = max(self.perm[self.c_idx1].copy())

        perm_temp = self.perm[self.c_idx1].copy()

        self.weight_arrangement = self.card_max(perm_temp, 5) - 3200

        self.helper_arr.append_weight_gen(self.weight_arrangement)

        if self.random == False:
            #self.print_arrengement()
            self.file.write("Wysoka karta: " + str(self.weight_arrangement) +
                            " Wysoka karta: " + self.high_card_1.print_str() +
                            " Numer: " + str(self.num_arr) + "\n")
                                
        self.num_arr += 1
            
        if self.example == True:
            self.print_arrengement()
            
            for idx in range(0, len(self.perm[self.c_idx1])):
                with open("permutations_data/high_card.txt", "a") as file:
                    file.write(self.perm[self.c_idx1][idx].print_str() + " ")
                    
            with open("permutations_data/high_card.txt", "a") as file:
                file.write("\n")
            
            with open("permutations_data/high_card.txt", "a") as file:
                file.write("Wysoka karta: " + str(self.weight_arrangement) + " Wysoka karta: " +
                            self.high_card_1.print_str() + " Numer: " + str(self.rand_int) + "\n")
                        
        return 1

    def high_card_generating(self, random, if_combs):
        self.random = random

        self.if_combs = if_combs
        
        if self.if_combs:        
            redis_buffer_instance.redis_1.set('min', '0')
            redis_buffer_instance.redis_1.set('max', self.max_combs)
        else:
            redis_buffer_instance.redis_1.set('min', '0')
            redis_buffer_instance.redis_1.set('max', self.max_1)
        
        cards_2d = []
        cards_to_comb_rest = []
        cards_comb_rest_sorted = []
        count = 0

        # Dodawanie talii do listy cards_2d
        for arrangement in self.cardmarkings.arrangements:
            for color in self.cardmarkings.colors:
                cards_2d.append(Card(arrangement, color))

    
        # Utworzenie kombinacji ukladow z talii kart
        self.cards_comb_rest = list(combinations(cards_2d, 5))
        
        # cards_to_comb_rest.clear()

        for idx in range(0, len(self.cards_comb_rest)):
            self.cards_comb_rest[idx] = list(self.cards_comb_rest[idx])
            
            #print(self.cards_comb_rest[idx])

            self.helper_arr.get_indices_1(self.cards_comb_rest[idx])
            self.helper_arr.get_indices_color(self.cards_comb_rest[idx])
            
            #print(len(self.helper_arr.get_indices_2d_1()))
            
            # Usuwanie ukladow ktore sa kolorem lub posiadaja wiecej takich samych figur niz 1
            for idx1, idx2 in zip(range(0, len(self.helper_arr.get_indices_2d_1())), 
                                  range(0, len(self.helper_arr.get_indices_2d_color()))):
                if len(self.helper_arr.get_indices_2d_1()[idx1]) > 1:
                    self.cards_comb_rest[idx] = []
                if len(self.helper_arr.get_indices_2d_color()[idx2]) == 5:
                    self.cards_comb_rest[idx] = []
            
            self.helper_arr.clear_indices_2d_1()
            self.helper_arr.clear_indices_2d_color()
            
            # Usuwanie ukladow ktore sa stritem
            for idx2, idx3 in zip(range(1, len(sorted(self.cards_comb_rest[idx]))),
                                    range(0, len(sorted(self.cards_comb_rest[idx])) - 1)):

                if (((sorted(self.cards_comb_rest[idx])[idx2].weight - sorted(self.cards_comb_rest[idx])[idx3].weight) == 1) or
                        (sorted(self.cards_comb_rest[idx])[4].weight == 13 and sorted(self.cards_comb_rest[idx])[4].weight -
                            sorted(self.cards_comb_rest[idx])[3].weight == 9)):
                    count += 1

                if count == 4:
                    self.cards_comb_rest[idx] = []
            count = 0

            # Usuwanie pustych list
            self.cards_comb_rest[idx] = list(filter(None, self.cards_comb_rest[idx]))
            # for idx, items in enumerate(self.cards_comb_rest):
            #     # Filter out None values and convert each element to a list if necessary
            #     self.cards_comb_rest[idx] = [list(item) if isinstance(item, tuple) else item for item in filter(None, items)]
            # for idx4 in range(0, len(self.cards_comb_rest[idx])):
            #     self.cards_comb_rest[idx][idx4].print()
            # print()
            if self.cards_comb_rest[idx] != []:
                if self.if_combs:
                    for idx4 in range(0, len(self.cards_comb_rest[idx])):
                        # self.cards_comb_rest[idx][idx4].print()
                        self.file.write(self.cards_comb_rest[idx][idx4].print_str() + " ")
                    self.file.write("\n")
                    self.file.flush()

                    self.c_idx1 = idx
                    self.num_arr_combs += 1
                    self.stop = self.loading_bar_combs.update_progress(self.num_arr)

                    if not self.stop:
                        self.helper_arr.check_if_weights_larger(show=False)
                        self.file.close()
                        return self.helper_arr.random_arrangement()
                
                    if not self.loading_bar_combs.check_stop_event():
                        sys.exit()
                    
                    self.arrangement_recogn()

                    self.helper_arr.append_cards_all_permutations(self.cards_comb_rest[idx])

                # for idx2 in range(0, len(cards_comb[idx1])):
                #     cards_comb[idx1][idx2].print()
                # print()
                    
                if not self.if_combs:
                    # Tworzenie permutacji kart z kombinacji
                    self.perm = list(permutations(self.cards_comb_rest[idx], 5))
                    for idx5 in range(0, len(self.perm)):
                        self.perm[idx5] = list(self.perm[idx5])
                        for idx2 in range(0, len(self.perm[idx5])):
                            #self.perm[idx5][idx2].print()
                            self.file.write(self.perm[idx5][idx2].print_str() + " ")
                        #print()
                        self.file.write("\n")
                        self.file.flush()
                        
                        # Zapisanie indeksu uzywanego w funkcji high_card()
                        self.c_idx1 = idx5
                        
                        self.stop = self.loading_bar_combs.update_progress(self.num_arr)
                        if not self.stop:
                            self.helper_arr.check_if_weights_larger(show=False)
                            self.file.close()
                            return self.helper_arr.random_arrangement()
                    
                        if not self.loading_bar.check_stop_event():
                            self.file.close()
                            sys.exit()

                        self.arrangement_recogn()
                            
                        self.helper_arr.append_cards_all_permutations(self.perm[idx5])
                        
                        self.iter_rand += 1

        self.helper_arr.check_if_weights_larger(show=False)

        self.file.close()
        
        return self.helper_arr.random_arrangement()