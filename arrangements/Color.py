from classes.Card import Card
from arrangements.HelperArrangement import HelperArrangement
from arrangements.CardMarkings import CardMarkings
from arrangements.LoadingBar import LoadingBar
from arrangements.HelperFileClass import HelperFileClass
from pathlib import Path
from itertools import permutations, combinations
from home.redis_buffer_singleton import redis_buffer_instance
import sys



class Color(HelperArrangement):
    
    def __init__(self):
        self.cardmarkings:CardMarkings = CardMarkings()  #Oznaczenia kart
        self.file_path = Path("permutations_data/color.txt")   
        self.file = open(self.file_path.resolve(), "w")
        self.helper_file_class = HelperFileClass(self.file_path.resolve())
        self.helper_arr = HelperArrangement(self.helper_file_class)
        
        self.max_value_generate:int = int(redis_buffer_instance.redis_1.get("entered_value").decode('utf-8'))

        self.loading_bar_1:LoadingBar = LoadingBar('color', self.max_value_generate, 100, 100, self.helper_arr)
        self.loading_bar_2:LoadingBar = LoadingBar('color_combs', self.max_value_generate, 100, 100, self.helper_arr)
        
        self.max_combs:str = str(int(self.loading_bar_1.total_steps/self.loading_bar_1.display_interval))
        self.max_1:str = str(int(self.loading_bar_2.total_steps/self.loading_bar_2.display_interval))
        
        self.cards_2d:list = []           # Przygotowanie listy do wstepnego przetwarzania
        self.perm:list = []               # Lista na permutacje
        self.perm_unsort:list = []        # Nieposortowana lista na permutacje

        self.high_card:Card = None        # Zmienna na wysoka kself.arte

        self.color_weight:int = 0        # Waga karty
        self.color_sum:int = 0           # Suma ukladu
        self.num_arr:int = 0             # Licznik
        self.count:int = 0               # Licznik pomocniczy do funkcji temp_lambda()
        self.count_1:int = 0             # Licznik do loading_bar()
        self.count_2:int = 0             # Licznik do loading_bar()
        self.c_idx2:int = 0

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
        if self.color_sum > 0:
            return self.color_sum

    def get_part_weight(self):
        return 0

    def temp_lambda(self, t1):
        #Jesli koniec sekwencji wag i sumy [[Card int] [Card int] ... [Card int] sum][[Card int] ... [Card int] sum]
        if self.count == 6:
            return

        self.count += 1

        #Zamiana indeksu kart (LISTA!) na string (SAMA LICZBA) (czyli self.count < 6, gdzie poczatek self.count zaczyna sie od 1)
        if self.count < 6:
            t2 = ''.join(map(str, t1[1]))
            if int(t2) < 5:
                return t1[1]
        #Zamiana wagi calego ukladu na string (bez listy)
        elif self.count == 6:
            t3 = ''.join(map(str, t1))
            if int(t3) > 4:
                return t1

    def print_arrengement(self):
        if self.random == False:
            print("Kolor:", self.color_sum, "Wysoka Karta:", self.high_card.print_str(), "Numer:", self.num_arr)
        elif self.random == True:
            print("Kolor:", self.color_sum, "Wysoka Karta:", self.high_card.print_str(), "Numer:", self.rand_int)

    def check_if_straight_royal_flush(self):
        #Sprawdzanie czy w ukladach kart znajduje sie Poker lub Poker Krolewski (do eliminacji)
        count = 0
        for idx, idx1 in zip(range(0, len(self.perm[self.c_idx2]) - 1), range(1, len(self.perm[self.c_idx2]))):
            #Karty musza byc poukladane od najmniejszej do najwiekszej w odstepie wartosci wagi wynoszacej 1
            #As jest traktowany jako najwyzsza karta lub najnizsza wtedy roznica miedzy A, a 2 wynosi 9
            if (sorted(self.perm[self.c_idx2])[idx1].weight - sorted(self.perm[self.c_idx2])[idx].weight == 1 or
                    (sorted(self.perm[self.c_idx2])[0].weight == 1 and sorted(self.perm[self.c_idx2])[4].weight == 13 and sorted(self.perm[self.c_idx2])[4].weight - self.perm[self.c_idx2][3].weight == 9)):
                count += 1
            if count == 4:
                return True

    def remove_straight_royal_flush(self):
        #Usuwanie Pokera oraz Pokera Krolewskiego

        calc_weights = True
        if_begin = False

        idx1 = 0
        idx2 = 0
        idx3 = 1
        straight_flush_iter = 0
        len_straight_flush_iter = 0
        len_iter = 0

        while (calc_weights):
            if straight_flush_iter == 0 and if_begin == True:
                idx2 = 0
                idx3 = 1
                if_begin = False
            elif if_begin == True:
                idx2 = 0
                idx3 = 1
                straight_flush_iter = 0
                if_begin = False

            #Dla posortowanej tablicy sprawdz czy waga jest mniejsza od kolejnej
            #Wykrywanie tych samych kart oraz strita
            if ((self.cards_2d[idx1][idx3].weight - self.cards_2d[idx1][idx2].weight == 1) or
                    #Wykrywanie kombinacji kart A 2 3 4 5
                    (self.cards_2d[idx1][0].weight == 1 and self.cards_2d[idx1][4].weight == 13 and self.cards_2d[idx1][4].weight - self.cards_2d[idx1][3].weight == 9)):
                straight_flush_iter += 1

            #Jesli zostaly sprawdzone 4 uklady to usun dany wiersz kart
            if straight_flush_iter == 4 and idx2 == 3:
                # for idx in range(0, len(self.cards_2d[idx1])):
                #     self.cards_2d[idx1][idx].print()
                # print()
                self.cards_2d.remove(self.cards_2d[idx1])

                idx2 = 0
                idx3 = 1
                straight_flush_iter = 0
                len_straight_flush_iter += 1
                if_begin = True

            elif idx2 == 3 and straight_flush_iter < 4:
                idx1 += 1
                idx2 = 0
                idx3 = 1
                if_begin = True
                straight_flush_iter = 0

            # print("cards_2d: ", len(self.cards_2d) * len(self.cardmarkings.colors))
            # print("len_iter: ", len_iter)
            # print("len_straight_flush_iter: ", len_straight_flush_iter)

            #Wyjscie z funkcji
            if ((len_iter + 1) - (len(self.cards_2d) * len(self.cardmarkings.colors))
                    == (len_straight_flush_iter * len(self.cardmarkings.colors))):
                calc_weights = False

            idx2 += 1
            idx3 += 1
            len_iter += 1

    def arrangement_recogn(self):
        #Obliczenia dla wyswietlenia ukladu losowego lub okreslonego (przykladowego)

        if self.example == True:
            self.c_idx2 = 0
            
            if len(self.helper_arr.dim(self.perm)) == 1:
                self.perm = [self.perm]
        
        if not self.if_combs:
            if self.check_if_straight_royal_flush():
                return
        
        if self.if_combs:
            self.perm = self.cards_2d.copy()
        
        self.color_weight = 0
        self.color_sum = 0
        self.helper_arr.clear_indices_2d_1()
        self.helper_arr.clear_indices_2d_color()
        
        #Pobranie indeksow tablicy, gdzie wystepuja takie same kolory
        self.helper_arr.get_indices_color(self.perm[self.c_idx2])
        self.helper_arr.get_indices_1(self.perm[self.c_idx2])
        
        for idx in range(0, len(self.helper_arr.get_indices_2d_1())):
            if len(self.helper_arr.get_indices_2d_1()[idx]) > 1:
                return
            
        #Lista ma dlugosc 1 w ktorej znajduje sie kolejna lista z kartami, a dalej z waga ukladu
        for idx1 in range(0, len(self.helper_arr.get_indices_2d_color()) - 4):
            #Jesli wystepuje 5 kolorow to jest to uklad Kolor
            if len(self.helper_arr.get_indices_2d_color()[idx1]) == 5:
                for idx in range(0, len(self.perm[self.c_idx2]) - 1):
                    #Dla kart innych niz najwyzsza policz czesciowo wage ukladu
                    if sorted(self.perm[self.c_idx2])[idx] != max(self.perm[self.c_idx2]):
                        #Potega od 1 do 4
                        #self.file.write("IDX: " + str(idx+1) + "weight: " + str(sorted(self.perm[self.c_idx2])[idx].weight) + "\n")
                        #print("IDX: ", idx+1, "weight: ", sorted(self.perm[self.c_idx2])[idx].weight)
                        
                        self.color_weight = pow(sorted(self.perm[self.c_idx2])[idx].weight, idx + 1)
                        self.color_sum += self.color_weight
                        #print(self.color_sum)
                self.high_card = max(self.perm[self.c_idx2])
                self.color_weight = pow(self.high_card.weight, 5)

                #Calkowita suma ukladu
                self.color_sum += self.color_weight + 12007274
                
                self.helper_arr.append_weight_gen(self.color_sum)
                
                if self.random == False:
                    #self.print_arrengement()
                    self.file.write("Kolor: " + str(self.color_sum) + " Wysoka Karta: " + self.high_card.print_str() + " Numer: " + str(self.num_arr) + "\n")              
                
                if self.example == True:
                    self.print_arrengement()
                    for idx in range(0, len(self.perm[self.c_idx2])):
                        with open("permutations_data/color.txt", "a") as file:
                            file.write(self.perm[self.c_idx2][idx].print_str() + " ")
                    with open("permutations_data/color.txt", "a") as file:
                        file.write("\n")
                    
                    with open("permutations_data/color.txt", "a") as file:
                        file.write("Kareta: " + str(self.color_sum) + " Numer: " + str(self.rand_int) + "\n")
                    
                
                self.num_arr += 1
                    
                return 6

    def color_generating(self, random, if_combs, session_id):
        self.random = random
        self.if_combs = if_combs
        
        self.helper_arr.set_session_id(session_id)
        self.loading_bar_1.set_session_id(session_id)
        self.loading_bar_2.set_session_id(session_id)

        if self.if_combs:     
            redis_buffer_instance.redis_1.set(f'min_{session_id}', '0')
            redis_buffer_instance.redis_1.set(f'max_{session_id}', self.max_combs)
        else:
            redis_buffer_instance.redis_1.set(f'min_{session_id}', '0')
            redis_buffer_instance.redis_1.set(f'max_{session_id}', self.max_1)

        self.cards_2d = []

        for idx in range(0, len(self.cardmarkings.colors)):
            self.cards_2d = []

            #Sprowadzenie kart do ukladu - 2Ki 3Ki 4Ki 5Ki 6Ki 7Ki 8Ki 9Ki 10Ki JKi QKi KKi AKi
            #                                                   ...
            for idx1 in self.cardmarkings.arrangements:
                self.cards_2d.append(Card(idx1, self.cardmarkings.colors[idx]))

            # for idx2 in range(0, len(self.cards_2d)):
            #     self.cards_2d[idx2].print()
            # print()

            self.cards_2d = list(combinations(self.cards_2d, 5))

            #Konwertowanie tuple do list
            self.cards_2d = [list(i) for i in self.cards_2d]

            #Usuwanie pokera oraz pokera krolewskiego
            self.remove_straight_royal_flush()
            
            if self.if_combs:
                # Wyswietlanie kombinacji wszystkich kart z ukladem kolor
                for idx1 in range(0, len(self.cards_2d)):
                    for idx2 in range(0, len(self.cards_2d[idx1])):
                        self.file.write(self.cards_2d[idx1][idx2].print_str() + " ")
                        # self.cards_2d[idx1][idx2].print()
                    self.file.write("\n")
                    # print()
                    
                    self.c_idx2 = idx1
                    self.arrangement_recogn()
                    self.file.flush()

                    if not self.loading_bar_2.update_progress(self.count_1):
                        self.helper_arr.check_if_weights_larger()
                        self.file.close()
                        return self.helper_arr.random_arrangement()
                   
                    if not self.loading_bar_2.check_stop_event():
                        sys.exit()
                        
                    self.count_1 += 1
                    
                    self.helper_arr.append_cards_all_permutations(self.perm[idx1])

            #Kazda iteracja zawiera 1278 kart dla kazdego koloru
            if not self.if_combs:
                for idx1 in range(0, len(self.cards_2d)):
                    self.perm = list(permutations(self.cards_2d[idx1], 5))

                    #Zamiana tuple na list w dwuwymiarowej tablicy
                    self.perm = [list(i) for i in self.perm]

                    #print(len(self.perm))
                    for idx2 in range(0, len(self.perm)):
                        if self.random == False:
                            for idx3 in range(0, len(self.perm[idx2])):
                                #self.perm[idx2][idx3].print()
                                self.file.write(self.perm[idx2][idx3].print_str() + " ")
                            #print()
                            self.file.write("\n")
                        self.file.flush()

                        self.c_idx2 = idx2
                        self.arrangement_recogn()

                        if not self.loading_bar_1.update_progress(self.count_1):
                            self.helper_arr.check_if_weights_larger()
                            self.file.close()
                            return self.helper_arr.random_arrangement()
                    
                        if not self.loading_bar_1.check_stop_event():
                            sys.exit()
                            
                        self.count_1 += 1
                        
                        self.helper_arr.append_cards_all_permutations(self.perm[idx2])
        
        self.helper_arr.check_if_weights_larger()

        self.file.close()
        
        return self.helper_arr.random_arrangement()