from classes.Card import Card
from arrangements.HelperArrangement import HelperArrangement
from arrangements.HelperFileClass import HelperFileClass
from arrangements.LoadingBar import LoadingBar
from arrangements.CardMarkings import CardMarkings
from home.redis_buffer_singleton import redis_buffer_instance
from itertools import permutations, combinations
from pathlib import Path
import sys

class ThreeOfAKind(HelperArrangement):
    
    def __init__(self):
        self.cardmarkings:CardMarkings = CardMarkings()  # Oznaczenia kart
        self.high_card:Card = Card()             # Wysoka karta (Card)
        
        self.file_path = Path("permutations_data/three_of_a_kind.txt")   
        self.file = open(self.file_path.resolve(), "w")
        self.helper_file_class = HelperFileClass(self.file_path.resolve())
        self.helper_arr = HelperArrangement(self.helper_file_class)
        
        self.max_value_generate:int = int(redis_buffer_instance.redis_1.get("entered_value").decode('utf-8'))
        if self.max_value_generate < 100:
            n_loading_bar = 1
        else:
            n_loading_bar = 100
        self.loading_bar:LoadingBar = LoadingBar('threeofakind', self.max_value_generate, n_loading_bar, n_loading_bar, self.helper_arr)
        self.loading_bar_combs:LoadingBar = LoadingBar('threeofakind_combs', self.max_value_generate, n_loading_bar, n_loading_bar, self.helper_arr)
        
        self.max_combs:str = str(int(self.loading_bar_combs.total_steps/self.loading_bar_combs.display_interval))
        self.max_1:str = str(int(self.loading_bar.total_steps/self.loading_bar.display_interval))
        
        self.perm:list = []                      # Lista na permutacje
        self.weight_arrangement_part:list = []   # Wagi wysokich kart

        self.weight_arrangement:int = 0         # Waga ukladu
        self.c_idx1:int = 0                     # Zapisywanie aktualnego indeksu z petli for
        self.num_arr:int = 0                    # Numer ukladu
        self.rand_int:int = 0

        self.random:bool = False                 # Czy uklad ma byc wylosowany
        self.example:bool = False                # Czy ma byc pokazany przykladowy uklad
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
            print("Trojka: ", self.weight_arrangement, "Wysoka karta: ", self.high_card.print_str(),  "Numer: ", self.num_arr)
        if self.random == True:
            print("Trojka: ", self.weight_arrangement, "Wysoka karta: ", self.high_card.print_str(),  "Numer: ", self.rand_int)

        self.num_arr += 1

    def remove_multiples(self, cards_comb):
        # Sprawdzanie oraz zapisanie indeksow powtarzajacych sie kart

        self.helper_arr.get_indices_1(cards_comb)

        for i in range(0, len(self.helper_arr.get_indices_2d_1())):
            if len(self.helper_arr.get_indices_2d_1()[i]) == 2:  # Jesli w wierszu tablicy znajduja sie 2 takie same elementy
                return True

        return False

    def remove_multiples_more_3(self, cards_comb):
        # Sprawdzanie oraz zapisanie indeksow powtarzajacych sie kart

        self.helper_arr.get_indices_1(cards_comb)

        for i in range(0, len(self.helper_arr.get_indices_2d_1())):
            if len(self.helper_arr.get_indices_2d_1()[i]) > 3:  # Jesli w wierszu tablicy znajduje wiecej niz 3 takie same elementy
                return True

        return False

    def arrangement_recogn(self):
        three_count_3 = 0       # Wiekszy o 1 gdy wystepuja 3 takie same karty
        three_count_1 = 0       # Wiekszy o 1 gdy wystepuje 1 taka sama karta
        once_2 = False          # Jesli prawda to procedura zostala wykonana (1 raz)
        once_1 = False          # Jesli prawda to procedura zostala wykonana (1 raz)
        three_weight = 0
        
       
        if self.if_combs:
            self.perm = self.cards_comb
        
        if not self.if_combs:
            if len(self.helper_arr.dim(self.perm)) == 1:
                self.perm = [self.perm]
                self.c_idx1 = 0
                self.helper_arr.clear_indices_2d_1()

        self.helper_arr.get_indices_1(self.perm[self.c_idx1])
        
        for idx in range(0, len(self.helper_arr.get_indices_2d_1())):

            # Jesli dlugosc jest rowna 3 to znaczy ze wystepuja 3 takie same karty
            if len(self.helper_arr.get_indices_2d_1()[idx]) == 3:
                three_count_3 += 1

                if once_1 == False:
                    three_weight += pow(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][0]].weight, 5)
                    three_weight += pow(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][1]].weight, 5)
                    three_weight += pow(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][2]].weight, 5)

                    once_1 = True

            # Jesli dlugosc jest rowna 1 to znaczy ze wystepuje 1 karta
            if len(self.helper_arr.get_indices_2d_1()[idx]) == 1:
                three_count_1 += 1

                if once_2 == False:
                    for idx1 in range(idx + 1, len(self.helper_arr.get_indices_2d_1())):
                        if len(self.helper_arr.get_indices_2d_1()[idx1]) == 1:

                            # Starsza karta otrzymuje wieksza wage
                            if self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][0]] < self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx1][0]]:
                                self.high_card = self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx1][0]]

                                three_weight += pow(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][0]].weight, 2)
                                self.weight_arrangement_part.append(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][0]].weight)

                                three_weight += pow(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx1][0]].weight, 3)
                                self.weight_arrangement_part.append(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx1][0]].weight)

                            else:
                                self.high_card = self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][0]]

                                three_weight += pow(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][0]].weight, 3)
                                self.weight_arrangement_part.append(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx][0]].weight)

                                three_weight += pow(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx1][0]].weight, 2)
                                self.weight_arrangement_part.append(self.perm[self.c_idx1][self.helper_arr.get_indices_2d_1()[idx1][0]].weight)

                    once_2 = True

        # Jesli prawda to uklad jest Trojka
        if three_count_3 == 3 and three_count_1 == 2:
            self.weight_arrangement = three_weight + 10126496
            self.helper_arr.append_weight_gen(self.weight_arrangement) # Tablica wag dla sprawdzania czy wygenerowane uklady maja wieksze
            if self.random == False:
                #self.print_arrengement()
                
                self.file.write("Trojka: " + str(self.weight_arrangement) + " Numer: " + str(self.num_arr) + "\n")

            if self.example == True:
                self.print_arrengement()
                
                for idx in range(0, len(self.perm[self.c_idx1])):
                    with open("permutations_data/three_of_a_kind.txt", "a") as file:
                        file.write(self.perm[self.c_idx1][idx].print_str() + " ")
                with open("permutations_data/three_of_a_kind.txt", "a") as file:
                    file.write("\n")
                
                with open("permutations_data/three_of_a_kind.txt", "a") as file:
                    file.write("Trojka: " + str(self.weight_arrangement) + " Numer: " + str(self.rand_int) + "\n")
                
            self.num_arr += 1
            
            return 4
        else:
            self.weight_arrangement = 0
            self.weight_arrangement_part = []

    def three_of_a_kind_generating(self, random, if_combs, session_id):
        self.random = random
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
        cards_to_comb = []
        cards_to_comb_1 = []
        cards_to_comb_rest = []
        i_three = 0
        iter_ar = 0
        len_comb = 0

        # Tworzenie talii kart
        for arrangement in self.cardmarkings.arrangements:
            for color in self.cardmarkings.colors:
                cards_2d.append(Card(arrangement, color))

        while (True):
            # for idx in range(0 + iter_ar, 4 + iter_ar):
            #     cards_2d[idx].print()
            # print("###############################")

            cards_to_comb_rest.extend(cards_2d[0:52])


            # for idx in range(0, len(cards_to_comb_rest)):
            #     cards_to_comb_rest[idx].print()
            # print()

            cards_comb_rest = list(combinations(cards_to_comb_rest, 2))

            cards_to_comb_rest.clear()

            for idx in range(0, len(cards_comb_rest)):
                # Rozszerza o 4 pierwsze karty z talii o takich samych figurach ale o roznych kolorach
                cards_to_comb.extend(cards_2d[0 + iter_ar : 4 + iter_ar])

                cards_comb_rest[idx] = list(cards_comb_rest[idx])

                # for idx1 in range(0, len(cards_comb_rest[idx])):
                #     cards_comb_rest[idx][idx1].print()
                # print()

                # Rozszerza o kombinacje 2 kart czyli jest 6 kart
                cards_to_comb.extend(cards_comb_rest[idx])

                cards_to_comb_1.append(cards_to_comb.copy())

                cards_to_comb.clear()

            # for idx in range(0, len(cards_to_comb_1)):
            #     for idx1 in range(0, len(cards_to_comb_1[idx])):
            #         cards_to_comb_1[idx][idx1].print()
            #     print()

            # Usuwanie gdy wystepuja 2 takie same karty oprocz ukladu ktory jest glowny (zostana usuniete w dalszym procesie)
            # Glowne karty: 2Ki 2Tr 2Pi 2Ka 2Ki 2Tr
            # Usuwane uklady. 2Ki 2Tr 2Pi 2Ka 3Ki 3Pi
            for idx in range(0, len(cards_to_comb_1)):
                if_remove_comb_1 = self.remove_multiples(cards_to_comb_1[idx])

                if if_remove_comb_1 == True:
                    cards_to_comb_1[idx] = []

                self.helper_arr.clear_indices_2d_1()

            cards_to_comb_1 = [x for x in cards_to_comb_1 if x != []]


            # for idx in range(0, len(cards_to_comb_1)):
            #     for idx1 in range(0, len(cards_to_comb_1[idx])):
            #         cards_to_comb_1[idx][idx1].print()
            #     print()

            for idx in range(0, len(cards_to_comb_1)):
                self.cards_comb = list(combinations(cards_to_comb_1[idx], 5))

                # Usuwanie wiersza gdy w ukladzie znajduja sie wiecej niz 3 takie same karty
                for idx1 in range(0, len(self.cards_comb)):
                    if_remove_comb_2 = self.remove_multiples_more_3(self.cards_comb[idx1])

                    if if_remove_comb_2 == True:
                        self.cards_comb[idx1] = []

                    self.helper_arr.clear_indices_2d_1()
                    
                    if self.if_combs:
                        if self.cards_comb[idx1] != []:
                            for idx6 in range(0, len(self.cards_comb[idx1])):
                                self.file.write(self.cards_comb[idx1][idx6].print_str() + " ")   
                            self.file.write("\n")
                            self.file.flush()

                            if not self.loading_bar_combs.update_progress(self.num_arr):
                                self.helper_arr.check_if_weights_larger(False)
                                self.file.close()
                                return self.helper_arr.random_arrangement()
                            
                            if not self.loading_bar_combs.check_stop_event():
                                sys.exit()

                            self.c_idx1 = idx1
                            self.arrangement_recogn()
                            
                            self.helper_arr.clear_indices_2d_1()
                            
                            self.helper_arr.append_cards_all_permutations(self.cards_comb[idx1])
                            
                self.cards_comb = [x for x in self.cards_comb if x != []]
              
                if not self.if_combs:
                    # Permutacje z gotowego uklady kombinacji
                    for idx1 in range(0, len(self.cards_comb)):
                        self.perm = list(permutations(self.cards_comb[idx1], 5))
                        #print(self.perm)

                        for idx1 in range(0, len(self.perm)):
                            self.perm[idx1] = list(self.perm[idx1])
                            for idx2 in range(0, len(self.perm[idx1])):
                                #self.perm[idx1][idx2].print()
                                self.file.write(self.perm[idx1][idx2].print_str() + " ")
                            #print()
                            self.file.write("\n")
                            self.file.flush()
                            
                            if not self.loading_bar.update_progress(self.num_arr):
                                self.helper_arr.check_if_weights_larger(False)
                                self.file.close()
                                return self.helper_arr.random_arrangement()
                            
                            if not self.loading_bar.check_stop_event():
                                sys.exit()
                            
                            # Pomocnicza, indeks do petli for w funkcji three_of_a_kind() - do listy perm
                            self.c_idx1 = idx1
                            self.arrangement_recogn()

                            self.helper_arr.clear_indices_2d_1()
                            
                            self.helper_arr.append_cards_all_permutations(self.perm[idx1])

                # Liczenie ilosci kombinacji
                len_comb += len(self.cards_comb)

            #print(len_comb)

            cards_to_comb_1.clear()

            # Liczenie iteracji
            i_three += 1
            iter_ar += 4

            # Jesli koniec ukladow to przerwij petle while
            if i_three == 13:
                break

        if self.random == False:
            self.helper_arr.check_if_weights_larger()
        
        self.file.close()
        
        return self.helper_arr.random_arrangement()