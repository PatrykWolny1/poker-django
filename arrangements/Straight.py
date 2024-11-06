from classes.Card import Card
from arrangements.HelperArrangement import HelperArrangement
from arrangements.HelperFileClass import HelperFileClass
from arrangements.LoadingBar import LoadingBar
from arrangements.CardMarkings import CardMarkings
from pathlib import Path
from home.redis_buffer_singleton import redis_buffer_instance
import itertools
import sys

class Straight(HelperArrangement):
    
    def __init__(self):
        self.cardmarkings:CardMarkings = CardMarkings()   #Oznaczenia kart
        
        self.file_path = Path("permutations_data/straight.txt")   
        self.file = open(self.file_path.resolve(), "w")
        self.helper_file_class = HelperFileClass(self.file_path.resolve())
        self.helper_arr = HelperArrangement(self.helper_file_class)
        
        self.max_value_generate:int = int(redis_buffer_instance.redis_1.get("entered_value").decode('utf-8'))
        
        self.loading_bar:LoadingBar = LoadingBar('straight', self.max_value_generate, 100, 100, self.helper_arr)
        self.loading_bar_combs:LoadingBar = LoadingBar('straight_combs', self.max_value_generate, 100, 100, self.helper_arr)

        self.max_combs:str = str(int(self.loading_bar_combs.total_steps/self.loading_bar_combs.display_interval))
        self.max_1:str = str(int(self.loading_bar.total_steps/self.loading_bar.display_interval))
        
        self.cards:list = []                      #Tablica na karty
        self.perm:list  = []                       #Tablica na permutacje do wag - posortowana
        self.cards_comb_list:list = []

        self.num_arr:int = 0                     #Liczenie ukladow kart w kolejnych iteracjach
        self.weight_arrangement:int = 0          #Zmienna pomocnicza do sumowania wagi ukladu
        self.straight_iter:int = 0               #Liczenie ile iteracji zostalo wykonanych
        self.c_idx6:int = 0
        self.c_idx6_iter:int = 0

        self.random:bool = False                  #Jesli jest losowanie ukladu
        self.example:bool = False                 #Jesli jest recznie wpisany uklad
    
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
        if self.random == False:
            print("Strit: ", self.weight_arrangement, " Numer: ", self.num_arr)
        if self.random == True:
            print("Strit: ", self.weight_arrangement, " Numer: ", self.rand_int)

        self.num_arr += 1

    def remove_royal_flush(self, cards_comb_list):
        # Pobranie indeksow kolorow czyli okreslenie indeksow w jakich wystepuja
        self.helper_arr.get_indices_color(cards_comb_list)

        for idx1 in range(0, len(self.get_indices_2d_color())):
            #Jesli wystepuje 5 kolorow w ukladzie
            if len(self.get_indices_2d_color()[idx1]) == 5:
                return True

        return False

    def remove_more_1(self, cards_comb_list):
        #Sprawdzanie oraz zapisanie indeksow powtarzajacych sie kart

        self.helper_arr.get_indices_1(cards_comb_list)

        for i in range(0, len(self.helper_arr.get_indices_2d_1())):
            if (len(self.helper_arr.get_indices_2d_1()[i]) > 1):  # Jesli w wierszu tablicy znajduje sie wiecej niz 1 element
                return True

        return False

    def arrangement_recogn(self):
        if self.if_combs:
            self.perm = self.cards_comb_list[self.c_idx6]
            
        if len(self.helper_arr.dim(self.perm)) == 1:
            self.perm = [self.perm]
            self.c_idx6 = 0
            self.c_idx6_iter = (120*1020) + 1
            if sorted(self.perm[self.c_idx6])[4].weight == 13 and sorted(self.perm[self.c_idx6])[3].weight == 4:
                self.c_idx6_iter = 0      
            self.helper_arr.clear_indices_2d_1()
            self.helper_arr.clear_indices_2d_color()
        
        # Przygotowanie tablicy do sortowania. Sortowanie jest uzywane zeby ulatwic okreslenie czy jest to strit
        #self.perm[self.c_idx6] = sorted(self.perm[self.c_idx6], key=lambda x: x.weight)
        # Pobranie indeksow gdzie wystepuja powtorzenia kolorow lub pojedynczy kolor

        self.helper_arr.get_indices_color(self.perm[self.c_idx6], random = True, example = True)
        self.helper_arr.get_indices_1(self.perm[self.c_idx6])

        # for idx1 in range(0, len(self.perm[self.c_idx6])):
        #     sorted(self.perm[self.c_idx6])[idx1].print()
        # print()

        weight_iter = 0
        straight_weight = 0
        calc_weights = True
        idx1 = 0
        idx2 = 1

        while (calc_weights):

            # Dla posortowanej tablicy sprawdz czy waga jest mniejsza od kolejnej
            for idx3, idx4 in zip(range(0, len(self.helper_arr.get_indices_2d_color())), range(0, len(self.helper_arr.get_indices_2d_1()))):
                # Jesli jest 5 takich samych kolorow to powrot z funkcji (poker krolewski)
                if len(self.helper_arr.get_indices_2d_color()[idx3]) == 5:
                    return
                if len(self.helper_arr.get_indices_2d_1()[idx4]) > 1:
                    return

            if idx1 == 4:
                break
            # Jesli waga pierwszej karty jest mniejsza od drugiej ... do 5 karty to jest to strit
            if ((sorted(self.perm[self.c_idx6])[idx2].weight - sorted(self.perm[self.c_idx6])[idx1].weight == 1) or
                    (sorted(self.perm[self.c_idx6])[4].weight == 13 and ((sorted(self.perm[self.c_idx6])[4].weight - sorted(self.perm[self.c_idx6])[3].weight) == 9))):

                if self.c_idx6_iter in range((120 * 1020) + 1): #120*1020
                    #print(idx1 + 2, sorted(self.perm[self.c_idx6])[idx1].print_str())
                    straight_weight += pow(sorted(self.perm[self.c_idx6])[idx1].weight, idx1 + 2)
                    weight_iter += 1

                    if sorted(self.perm[self.c_idx6])[idx2].weight == 13:
                        #print("1", sorted(self.perm[self.c_idx6])[idx2].print_str())
                        straight_weight += pow(sorted(self.perm[self.c_idx6])[idx2].weight, 1)
                        weight_iter += 1

                else:
                    #print(idx1 + 1, sorted(self.perm[self.c_idx6])[idx1].print_str())
                    straight_weight += pow(sorted(self.perm[self.c_idx6])[idx1].weight, idx1 + 1)
                    weight_iter += 1
                    #print(straight_weight)

                    if idx2 == 4:
                        #print(idx2 + 1, sorted(self.perm[self.c_idx6])[idx2].print_str())
                        straight_weight += pow(sorted(self.perm[self.c_idx6])[idx2].weight, idx2 + 1)
                        weight_iter += 1
                        #print(straight_weight)

                # Jesli jest strit to weight_iter == 4. Liczono od 0
                if weight_iter == 5:
                    self.weight_arrangement = straight_weight + 11242224
                    self.helper_arr.append_weight_gen(self.weight_arrangement)
                    
                    if self.random == False:
                        #self.print_arrengement()

                        self.file.write("Strit: " + str(self.weight_arrangement) + " Numer: " + str(self.num_arr) + "\n")
                                               
                
                    if self.example == True:
                        self.print_arrengement()

                        for idx in range(0, len(self.perm[self.c_idx6])):
                            with open("permutations_data/straight.txt", 'a') as file:
                                file.write(self.perm[self.c_idx6][idx].print_str() + " ")
                        with open("permutations_data/straight.txt", 'a') as file:
                            file.write("\n")
                                        
                        with open("permutations_data/straight.txt", 'a') as file:
                            file.write("Strit: " + str(self.weight_arrangement) + " Numer: " + str(self.rand_int) + "\n")

                    self.num_arr += 1
                    
                    calc_weights = False

                    return 5

            idx1 += 1
            idx2 += 1

    def straight_generating(self, random, if_combs):
        self.random = random
        self.if_combs = if_combs
        
        if self.if_combs:        
            redis_buffer_instance.redis_1.set('min', '0')
            redis_buffer_instance.redis_1.set('max', self.max_combs)
        else:
            redis_buffer_instance.redis_1.set('min', '0')
            redis_buffer_instance.redis_1.set('max', self.max_1)
        
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
                            cards_1d.append(Card(self.cardmarkings.arrangements[len(self.cardmarkings.arrangements) - 1], color))
                        if idx1 < 4:
                            cards_1d.append(Card(self.cardmarkings.arrangements[idx1], color))
                    else:
                        cards_1d.append(Card(self.cardmarkings.arrangements[idx1 + m], color))
                if color == 'Ka':
                    cards_2d.append(cards_1d[:])

        # for idx3 in range(0, len(cards_2d)):
        #     for idx4 in range(0, len(cards_2d[idx3])):
        #         cards_2d[idx3][idx4].print()
        #     print()

        return self.check_generate_cards(cards_2d)

    def check_generate_cards(self, cards_2d):
        #Generowanie 5 kart oraz sprawdzanie jaki to uklad
        self.cards_comb_list = []

        self.permutation = True

        for idx1 in range(0, len(cards_2d)):
            self.cards.clear()
            for idx2 in range(0, len(cards_2d[idx1])):
                self.cards.append(cards_2d[idx1][idx2])
                if idx2 == 19:
                    if self.permutation:
                        cards_comb = list(itertools.combinations(self.cards, 5))

                        self.cards_comb_list.clear()

                        for idx5 in cards_comb:
                            self.cards_comb_list.append(list(idx5))

                        #Usuwanie z tablicy kombinacji kart o ilosci wiekszej od 1

                        for idx5 in range(0, len(self.cards_comb_list)):
                            # Usuwanie ukladow gdzie wystepuje wiecej niz 1 taka sama karta
                            if_remove = self.remove_more_1(self.cards_comb_list[idx5])
                            #Usuwanie pokera krolewskiego z permutacji ukladow
                            if_remove_rf = self.remove_royal_flush(self.cards_comb_list[idx5])

                            if if_remove == True or if_remove_rf == True:
                                self.cards_comb_list[idx5] = []

                            self.helper_arr.clear_indices_2d_1()
                            self.helper_arr.clear_indices_2d_color()

                        # self.cards_comb_list = [ele for ele in self.cards_comb_list if ele != []]
                        
                        if self.if_combs:
                            for idx55 in range(0, len(self.cards_comb_list)):
                                if self.cards_comb_list[idx55] != []:
                                    for idx6 in range(0, len(self.cards_comb_list[idx55])):
                                        self.file.write(self.cards_comb_list[idx55][idx6].print_str() + " ")   
                                    self.file.write("\n")
                                                                   
                                    self.c_idx6 = idx55
                                    self.arrangement_recogn()
                                    
                                    self.helper_arr.clear_indices_2d_1()

                                    if not self.loading_bar_combs.update_progress(self.straight_iter):
                                        self.helper_arr.check_if_weights_larger(False)
                                        return self.helper_arr.random_arrangement()
                                    
                                    if not self.loading_bar_combs.check_stop_event():
                                        sys.exit()
                                    self.helper_arr.append_cards_all_permutations(self.cards_comb_list[idx55])
                                    self.straight_iter += 1

                        # for idx5 in range(0, len(self.cards_comb_list)):
                        #     for idx6 in range(0, len(self.cards_comb_list[idx5])):
                        #         self.cards_comb_list[idx5][idx6].print()
                        #     print()

                        #print(len(self.cards_comb_list))
                        if not self.if_combs: 
                            for idx5 in self.cards_comb_list:
                                self.perm = list(itertools.permutations(idx5, 5))

                                for idx6 in range(0, len(self.perm)):
                                    self.perm[idx6] = list(self.perm[idx6])

                                    self.helper_arr.get_indices_1(self.perm[idx6])

                                    if self.random == False:
                                        for idx7 in range(0, len(self.perm[idx6])):
                                            #self.perm[idx6][idx7].print()
                                            self.file.write(self.perm[idx6][idx7].print_str() + " ")
                                        #print()
                                        self.file.write("\n")

                                    self.c_idx6 = idx6
                                    self.arrangement_recogn()

                                    self.helper_arr.clear_indices_2d_1()


                                    if not self.loading_bar.update_progress(self.straight_iter):
                                        self.helper_arr.check_if_weights_larger(False)
                                        return self.helper_arr.random_arrangement()
                                    
                                    if not self.loading_bar.check_stop_event():
                                        sys.exit()
                                
                                    self.helper_arr.append_cards_all_permutations(self.perm[idx6])
                                    self.straight_iter += 1

                                    self.c_idx6_iter += 1

        self.helper_arr.check_if_weights_larger()

        self.file.close()
        
        return self.helper_arr.random_arrangement()
