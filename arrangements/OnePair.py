from arrangements.HelperArrangement import HelperArrangement
from arrangements.HelperFileClass import HelperFileClass
from classes.Card import Card
from arrangements.LoadingBar import LoadingBar
from arrangements.CardMarkings import CardMarkings
from itertools import permutations, combinations
from pathlib import Path
from home.redis_buffer_singleton import redis_buffer_instance
import sys

class OnePair(HelperArrangement):
    
    def __init__(self):
        self.cardmarkings:CardMarkings = CardMarkings()  # Oznaczenia kart
        self.high_card:Card = Card()             # Wysoka karta
        self.limit_rand:int = 1000             # Ograniczenie dla liczby obliczen  
        self.one_iter:int = 120
        self.n_combs = 1098240
        self.file_path = Path("permutations_data/one_pair.txt")   
        self.file = open(self.file_path.resolve(), "w")
        self.helper_file_class = HelperFileClass(self.file_path.resolve())
        self.helper_arr = HelperArrangement(self.helper_file_class)
        
        self.max_value_generate:int = int(redis_buffer_instance.redis_1.get("entered_value").decode('utf-8'))

        self.loading_bar:LoadingBar = LoadingBar('onepair', self.max_value_generate, 100, 100, self.helper_arr) #Permutacje: 131 788 800
        self.loading_bar_combs:LoadingBar = LoadingBar('onepair_combs', self.max_value_generate, 100, 100, self.helper_arr)              #Kombinacje: 1 098 240 2s -> 84480

        self.max_combs:str = str(int(self.loading_bar_combs.total_steps/self.loading_bar_combs.display_interval))
        self.max_1:str = str(int(self.loading_bar.total_steps/self.loading_bar.display_interval))
        
        self.perm:list = []                      # Lista na permutacje
        self.weight_arrangement_part:list  = []   # Lista na wagi pozostalych kart   
        self.cards_comb:list = []

        self.weight_arrangement:int = 0         # Waga ukladu
        self.c_idx1:int = 0                     # Zapisywanie aktualnego indeksu z petli for
        self.num_arr:int = 0                    # Numer ukladu
        self.rand_iter:int = 0

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
        # Jesli to jest to aktualny uklad to zwroc wage ukladu
        if self.weight_arrangement > 0:
            return self.weight_arrangement

    def get_part_weight(self):
        if sum(self.weight_arrangement_part) > 0:
            return self.weight_arrangement_part

    def print_arrengement(self):
        if self.random == False:
            print("Jedna Para: ", self.weight_arrangement, "Wysoka karta: ", self.high_card.print_str(),  "Numer: ", self.num_arr)
        if self.example == True:
            print("Jedna Para: ", self.weight_arrangement, "Wysoka karta: ", self.high_card.print_str(),  "Numer: ", self.rand_int)

    def remove_multiples(self, cards_comb):
        # Sprawdzanie oraz zapisanie indeksow powtarzajacych sie kart

        for i in range(0, len(self.helper_arr.get_indices_2d_1())):
            if len(self.helper_arr.get_indices_2d_1()[i]) in range(2, 4):  # Jesli w wierszu tablicy znajduja sie 2 lub 3 takie same elementy
                return True

        return False

    def remove_multiples_more_4(self, cards_comb):
        # Sprawdzanie oraz zapisanie indeksow powtarzajacych sie kart

        for i in range(0, len(self.helper_arr.get_indices_2d_1())):
            if len(self.helper_arr.get_indices_2d_1()[i]) > 4:  # Jesli w wierszu tablicy znajduja sie wiecej niz 4 takie same elementy
                return True

        return False

    def remove_multiples_more_2(self, cards_comb):
        # Sprawdzanie oraz zapisanie indeksow powtarzajacych sie kart

        for i in range(0, len(self.helper_arr.get_indices_2d_1())):
            if len(self.helper_arr.get_indices_2d_1()[i]) > 2:  # Jesli w wierszu tablicy znajduja sie wiecej niz 2 takie same elementy
                return True

        return False

    def arrangement_recogn(self):
        one_count_1 = 0     # Licznik na uklad wysoka karta
        one_count_2 = 0     # Licznik na uklad para
        once_1 = False      # Zmienne ktore sluza do wykonania petli jeden raz
        once_2 = False
        once_3 = False
        one_weight = 0          # Waga ukladu
        cards_max_sort = []     # Lista na karty do okreslenie najwyzszej karty (na pojedyncze karty)
        self.weight_arrangement_part = []
        
        if len(self.helper_arr.dim(self.perm)) == 1:
            self.perm = [self.perm]
            self.c_idx1 = 0
        
        if self.if_combs:
            self.perm = self.cards_comb
            
        self.helper_arr.clear_indices_2d_1()
        self.helper_arr.get_indices_1(self.perm[self.c_idx1])
        
        for idx in range(0, len(self.helper_arr.get_indices_2d_1())):
            if len(self.helper_arr.get_indices_2d_1()[idx]) == 2:
                one_count_2 += 1

                # Warunek wykonywany jeden raz
                if once_1 == False:
                    # Obliczenia dla jednej karty i drugiej (para)
                    one_weight += pow(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][0]].weight, 6)
                    one_weight += pow(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][1]].weight, 6)

                    once_1 = True

            if len(self.helper_arr.get_indices_2d_1()[idx]) == 1:
                # Dodanie do listy karty ktorej wystapienie pojawia sie 1 raz w ukladzie
                cards_max_sort.append(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][0]])
                one_count_1 += 1

                # Wyszukiwanie w kolejnych petlach kart ktore wystepuja 1 raz w ukladzie
                for idx1 in range(idx + 1, len(self.helper_arr.get_indices_2d_1())):

                    if once_2 == False:

                        if len(self.helper_arr.get_indices_2d_1()[idx1]) == 1:
                            cards_max_sort.append(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx1][0]])

                            for idx2 in range(idx1 + 1, len(self.helper_arr.get_indices_2d_1())):
                                if len(self.helper_arr.get_indices_2d_1()[idx2]) == 1:
                                    cards_max_sort.append(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx2][0]])

                                    if once_3 == False:
                                        cards_max_sort.sort(key=lambda x: x.weight)

                                        # Znalezienie minimalnej i maksymalnej wagi karty z posrod 3 kart
                                        min_card = cards_max_sort.index(min(cards_max_sort))
                                        self.high_card = cards_max_sort.index(max(cards_max_sort))

                                        # Wyszukanie srodkowej wagi karty z posrod 3 kart (wyszukiwanie po indeksach)
                                        for idx3 in range(0, len(cards_max_sort)):
                                            # Jesli indeks idx3 nie jest rowny indeksom min i max to jest to waga srodkowa
                                            if idx3 not in [min_card, self.high_card]:
                                                mid_card = cards_max_sort[idx3]
                                                one_weight += pow(mid_card.weight, 3)
                                            #cards_max_sort[idx3].print()
                                        #print()

                                        self.high_card = max(cards_max_sort)
                                        min_card = min(cards_max_sort)

                                        one_weight += pow(min_card.weight, 2)
                                        one_weight += pow(self.high_card.weight, 4)

                                        # print("Min: ", min_card.print_str())
                                        # print("Mid: ", mid_card.print_str())
                                        # print("Max: ", self.high_card.print_str())

                                        cards_max_sort.clear()

                                        once_3 = True
                            once_2 = True

        # Jesli pojedyncza karta wystepuje 3 razy oraz wystepuje 1 para to zakoncz
        if one_count_1 == 3 and one_count_2 == 2:
            self.weight_arrangement = one_weight + 390079

            self.helper_arr.append_weight_gen(self.weight_arrangement)   # Tablica wag dla sprawdzania czy wygenerowane uklady maja wieksze
            
            if self.random == False:
                #self.print_arrengement()
                self.file.write("Jedna para: " + str(self.weight_arrangement) +
                                " Wysoka Karta: " + self.high_card.print_str() +
                                " Numer: " + str(self.num_arr) + "\n")
                                    
            self.num_arr += 1
                
            if self.example == True:
                self.print_arrengement()
                
                for idx in range(0, len(self.perm[self.c_idx1])):
                    with open("permutations_data/one_pair.txt", "a") as file:
                        file.write(self.perm[self.c_idx1][idx].print_str() + " ")
                        
                with open("permutations_data/one_pair.txt", "a") as file:
                    file.write("\n")
                
                with open("permutations_data/one_pair.txt", "a") as file:
                    file.write("Jedna Para: " + str(self.weight_arrangement) + " Wysoka karta: " +
                                    self.high_card.print_str() + " Numer: " + str(self.rand_int) + "\n")
                
                self.weight_arrangement_part.append(min_card.weight)
                self.weight_arrangement_part.append(mid_card.weight)
                self.weight_arrangement_part.append(self.high_card.weight)
                return 2

        else:
            self.weight_arrangement = 0
            self.weight_arrangement_part = []


    def one_pair_generating(self, random, if_combs):
        self.random = random
        self.if_combs = if_combs
        
        if self.if_combs:        
            redis_buffer_instance.redis_1.set('min', '0')
            redis_buffer_instance.redis_1.set('max', self.max_combs)
        else:
            redis_buffer_instance.redis_1.set('min', '0')
            redis_buffer_instance.redis_1.set('max', self.max_1)
        
        cards_2d = []
        cards_to_comb = []
        cards_to_comb_1 = []
        cards_to_comb_rest = []
        arr_iter = 0     # Kolejne iteracje dla kolejnych serii ukladow
        len_comb = 0    # Ilosc kombinacji

        # Tworzenie talii kart
        for arrangement in self.cardmarkings.arrangements:
            for color in self.cardmarkings.colors:
                cards_2d.append(Card(arrangement, color))

        # #while (True):
        # for idx in range(0, len(cards_2d)):
        #     cards_2d[idx].print()
        # print("###############################")

        cards_to_comb_rest = cards_2d.copy()
        
        # for idx in range(0, len(cards_to_comb_rest)):
        #     cards_to_comb_rest[idx].print()
        # print()

        # Tworzenie kombinacji 3 kart (maja byc pojedyncze)
        cards_comb_rest = list(combinations(cards_to_comb_rest.copy(), 3))

        # for idx in range(0, len(cards_comb_rest)):
        #     for idx1 in range(0 ,len(cards_comb_rest[idx])):
        #         cards_comb_rest[idx][idx1].print()
        #     print()
        idx_1 = 0
        while(True):
            if idx_1 == len(cards_comb_rest):
                break
            
            self.helper_arr.clear_indices_2d_1()

            self.helper_arr.get_indices_1(cards_comb_rest[idx_1])
            
            # Usuwanie powtorek powtarzajacych sie kart (2 lub 3)
            if_remove_comb_1 = self.remove_multiples(cards_comb_rest[idx_1])
            
            if if_remove_comb_1 == True:
                cards_comb_rest[idx_1] = []
                cards_comb_rest = list(filter(None, cards_comb_rest))
                idx_1 -= 1
            
            # for idx2 in range(0, len(cards_comb_rest[idx_1])):
            #     cards_comb_rest[idx_1][idx2].print()
            # print()  
              
            idx_1 += 1

        for idx1 in range(0, len(self.cardmarkings.arrangements)):
            for idx in range(0, len(cards_comb_rest)):
            
            #for idx in range(0, len(cards_comb_rest)):
            
                cards_comb_rest[idx] = list(cards_comb_rest[idx])

                cards_to_comb.extend(cards_2d[0 + arr_iter:4 + arr_iter])
                cards_to_comb.extend(cards_comb_rest[idx])
                
                # for idx2 in range(0, len(cards_to_comb)):
                #     cards_to_comb[idx2].print()
                # print()
                
                cards_to_comb_1.append(cards_to_comb.copy())
                cards_to_comb.clear()
                
            arr_iter += 4

        # for idx2 in range(0, len(cards_to_comb_1)):
        #     for idx3 in range(0, len(cards_to_comb_1[idx2])):
        #         cards_to_comb_1[idx2][idx3].print()
        #     print() 

        idx_1 = 0
        while(True):
            #print(idx_1)
            if idx_1 == len(cards_to_comb_1):
                break
            
            self.helper_arr.clear_indices_2d_1()
            self.helper_arr.get_indices_1(cards_to_comb_1[idx_1])
            
            # Usuwanie powtorek powtarzajacych sie kart (2 lub 3)
            if_remove_comb_1 = self.remove_multiples(cards_to_comb_1[idx_1])
            if_remove_comb_2 = self.remove_multiples_more_4(cards_to_comb_1[idx_1])

            if if_remove_comb_1 == True:
                cards_to_comb_1[idx_1] = []
            
            if if_remove_comb_2 == True:
                cards_to_comb_1[idx_1] = []
                
            idx_1 += 1
            
        cards_to_comb_1 = list(filter(None, cards_to_comb_1))                

        # for idx2 in range(0, len(cards_to_comb_1)):
        #     for idx3 in range(0, len(cards_to_comb_1[idx2])):
        #         cards_to_comb_1[idx2][idx3].print()
        #     print()                 
                
                
        idx_2 = 0
        for idx in range(0, len(cards_to_comb_1)):
            self.cards_comb = list(combinations(cards_to_comb_1[idx], 5))
            
            for idx1 in range(0, len(self.cards_comb)):
                
                self.helper_arr.clear_indices_2d_1()
                self.helper_arr.get_indices_1(self.cards_comb[idx1])
                
                if_remove_comb_3 = self.remove_multiples_more_2(self.cards_comb[idx1])
                
                if if_remove_comb_3 == True:
                    self.cards_comb[idx1] = []
                
            self.cards_comb = list(filter(None, self.cards_comb))                
            
            #for idx1 in range(0, len(self.cards_comb)):
                # for idx2 in range(0, len(self.cards_comb[idx1])):
                #     self.cards_comb[idx1][idx2].print()
                # print()
                
            for idx1 in range(0, len(self.cards_comb)):
                self.perm = list(permutations(self.cards_comb[idx1], 5))

                len_comb += 1
                
                if self.if_combs:
                    self.cards_comb[idx1] = list(self.cards_comb[idx1])
                    
                    # # Test if cards arrangement is one pair of 2s or 3s ... As
                    # for idx2 in range(0, len(self.cards_comb[idx1])):
                    #     with open("permutations_data/one_pair.txt", "a") as file:
                    #         file.write(self.cards_comb[idx1][idx2].print_str() + " ")
                    # with open("permutations_data/one_pair.txt", "a") as file:
                    #     file.write("\n")
                    #     if self.cards_comb[idx1][0].weight == 2:
                    #         with open("permutations_data/one_pair.txt", "a") as file:
                    #             file.write(self.cards_comb[idx1][idx2].print_str() + " ")
                    #         with open("permutations_data/one_pair.txt", "a") as file:
                    #             file.write(str(len_comb))
                    #         print("END")
                    #         time.sleep(1000)

                    # Test if cards arrangement is one pair of 2s or 3s ... As
                    # pickle.dump(self.cards_comb[idx1], self.pickle_data, pickle.HIGHEST_PROTOCOL)

                    for idx2 in range(0, len(self.cards_comb[idx1])):
                        self.file.write(self.cards_comb[idx1][idx2].print_str() + " ")
                    self.file.write("\n")
                    
                    self.file.flush()

                    if not self.loading_bar_combs.update_progress(len_comb):
                        self.helper_arr.check_if_weights_larger(False)
                        self.file.close()
                        return self.helper_arr.random_arrangement()
                
                    if not self.loading_bar_combs.check_stop_event():
                        sys.exit()

                    self.c_idx1 = idx1
                    self.arrangement_recogn()
                    
                    self.helper_arr.append_weight_gen(0)
                    self.helper_arr.append_cards_all_permutations(self.cards_comb[idx1])
            
                        
                    # if len_comb == self.n_combs:                #84480    One pair of 2s
                    #     print("END")
                    #     # print(len_comb)
                    #     # self.file.write(str(len_comb))
                    #     # self.file_data.close()
                    #     self.file.close()
                        
                    #     return self.helper_arr.random_arrangement(self.if_combs)
        
                # for idx2 in range(0, len(self.cards_comb[idx1])):
                #     self.cards_comb[idx1][idx2].print()
                # print()
                if not self.if_combs:
                    for idx2 in range(0, len(self.perm)):
                        self.perm[idx2] = list(self.perm[idx2])
                        idx_2 += 1
                        if self.random == False:
                            for idx3 in range(0, len(self.perm[idx2])):
                                #self.perm[idx2][idx3].print()
                                self.file.write(self.perm[idx2][idx3].print_str() + " ")
                            #print()
                            self.file.write("\n")
                        self.file.flush()
                        # Zapisanie indeksu uzywanego w funkcji one_pair()


                        if not self.loading_bar.update_progress(self.num_arr):
                            self.helper_arr.check_if_weights_larger(False)
                            self.file.close()
                            return self.helper_arr.random_arrangement()
                    
                        if not self.loading_bar.check_stop_event():
                            sys.exit()
                        
                        self.c_idx1 = idx2
                        self.arrangement_recogn()
                          
                        self.helper_arr.append_cards_all_permutations(self.perm[idx2])

            
                        # self.rand_iter += 1
                        #print(self.rand_iter) 
            
                        # if self.rand_iter == self.one_iter * self.limit_rand:
                        #     self.helper_arr.check_if_weights_larger(False)
                        #     #print(len_comb)
                        #     self.file.close()
                            
                        #     return self.helper_arr.random_arrangement(False)


        self.helper_arr.check_if_weights_larger(False)

        self.file.close()

        return self.helper_arr.random_arrangement()