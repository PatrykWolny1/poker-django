from classes.Card import Card
from arrangements.HelperArrangement import HelperArrangement
from arrangements.HelperFileClass import HelperFileClass
from arrangements.LoadingBar import LoadingBar
from arrangements.CardMarkings import CardMarkings
from home.redis_buffer_singleton import redis_buffer_instance
from pathlib import Path
import itertools
import sys

class Carriage(HelperArrangement):
    
    def __init__(self):
        self.file_path = Path("permutations_data/carriage.txt")   
        self.file = open(self.file_path.resolve(), "w")
        self.helper_file_class = HelperFileClass(self.file_path.resolve())
        self.helper_arr = HelperArrangement(self.helper_file_class)
        self.cardmarkings = CardMarkings()   #Oznaczenia kart
        self.loading_bar = LoadingBar('carriage', 74880, 20, 19, self.helper_arr) #Permutacje
        self.loading_bar_combs = LoadingBar('carriage_combs', 624, 60, 60, self.helper_arr)   #Kombinacje
        
        self.max_combs:str = str(int(self.loading_bar_combs.total_steps/self.loading_bar_combs.display_interval))
        self.max_1:str = str(int(self.loading_bar.total_steps/self.loading_bar.display_interval))

        self.cards:list = []                      #Tablica do wstepnego przetwarzania
        self.cards_2d:list = []                   #Tablica do wstepnego przetwarzania
        self.cards_5:list = []                    #Tablca do wstepnego przetwarzania
        self.cards_perm:list = []                 #Tablica na permutacje
        self.combs:list = []                      #Tablica na kombinacje
        self.cards_perm:list = []                 #Tablica do obliczania wag w funkcji carriage()
        
        self.rand_int:int = 0
        self.num_arr:int = 0                     #Licznik ilosci ukladow
        self.weight_arrangement_part:int = 0     #Waga ostatniej karty
        self.weight_arrangement:int = 0          #Waga ukladu
        self.c_idx6:int = 0

        self.if_perm_weights:bool = True
        self.print_permutations:bool = True       #Wyswietlanie wszystkich permutacji
        self.example:bool = False                 #Jesli jest recznie wpisany uklad
        self.random:bool = False                  #Jesli jest losowanie ukladu
        self.if_combs:bool = False
        self.stop:bool = True
        
    #Funkcja dla przykladowego ukladu wpisanego recznie
    def set_cards(self, cards):
        self.cards_perm = cards
        self.example = True
        self.random = True

    def set_rand_int(self, rand_int):
        self.rand_int = rand_int
        
    def get_weight(self):
        if self.weight_arrangement > 0:
            return self.weight_arrangement

    def get_part_weight(self):
        if self.weight_arrangement_part > 0:
            return self.weight_arrangement_part

    def print_arrengement(self):
        if self.example == True:
            print("Kareta: ", self.weight_arrangement)#, "Numer: ", self.rand_int)
        if self.random == False:
            print("Kareta: ", self.weight_arrangement)#, "Numer: ", self.rand_int)

    def arrangement_recogn(self, combs=[]):
        # Sprawdzanie czy uklad kart to kareta oraz przypisanie wagi do ukladu
        if self.if_combs:
            self.cards_perm = [combs]
        
        if self.example == True:
            self.c_idx6 = 0
            
            if len(self.helper_arr.dim(self.cards_perm)) == 1:
                self.cards_perm = [self.cards_perm]
        
        self.helper_arr.clear_indices_2d_1()
        self.helper_arr.get_indices_1(self.cards_perm[self.c_idx6])

        # if self.if_perm_weights:
        #     self.cards_perm_weights = []
        #     # Sprawdzanie czy tablica indeksow nie jest pusta
        #     if len(HelperArrangement().get_indices_2d_1()) != 0:
        #         for idx1 in self.cards_perm:
        #             # Zapisanie ukladow w innej tablicy bo tablica self.cards_perm jest zerowana w check_generate_cards
        #             self.cards_perm_weights.append(Card(idx1.name, idx1.color))
        # else:
        #     HelperArrangement().get_indices_1(self.cards_perm_weights)

        if_carriage = 0
        weight_1 = 0
        weight_2 = 0

        # Waga ukladu
        self.weight_arrangement = 0
        
        try:
            for i in range(0, len(self.helper_arr.get_indices_2d_1())):
                # print("Rozmiar: ", len(self.indeksy_2d[i]))
                # Jesli w wierszu tablicy znajduja sie 4 elementy | Indeksy powtorek, jesli jest kareta to dlugosc = 4
                if (len(self.helper_arr.get_indices_2d_1()[i]) == 4):
                    for j in range(0, len(self.helper_arr.get_indices_2d_1()[i])):
                        weight_1 = pow(self.cards_perm[self.c_idx6][self.helper_arr.get_indices_2d_1()[i][j]].weight, 4)
                    if_carriage += 1

                # Ostatnia karta
                if (len(self.helper_arr.get_indices_2d_1()[i]) == 1):
                    for j in range(0, len(self.helper_arr.get_indices_2d_1()[i])):
                        weight_2 = self.cards_perm[self.c_idx6][self.helper_arr.get_indices_2d_1()[i][j]].weight * 1

                        self.weight_arrangement_part = self.cards_perm[self.c_idx6][self.helper_arr.get_indices_2d_1()[i][j]].weight
                
                if (i == len(self.helper_arr.get_indices_2d_1()) - 1) and (if_carriage == 4):
                    self.weight_arrangement = (weight_1 + weight_2) + 12415456
                    self.helper_arr.append_weight_gen(self.weight_arrangement)
                    
                    if self.random == False:
                        #self.print_arrengement()
                        
                        self.file.write("Kareta: " + str(self.weight_arrangement) + " Numer: " + str(self.num_arr) + "\n")

                    if self.example == True:
                        self.print_arrengement()
                        
                        for idx in range(0, len(self.cards_perm[self.c_idx6])):
                            with open("permutations_data/carriage.txt", "a") as file:
                                file.write(self.cards_perm[self.c_idx6][idx].print_str() + " ")
                        with open("permutations_data/carriage.txt", "a") as file:
                            file.write("\n")
                        
                        with open("permutations_data/carriage.txt", "a") as file:
                            file.write("Kareta: " + str(self.weight_arrangement) + " Numer: " + str(self.rand_int) + "\n")
                        
                    self.num_arr += 1
                            
                    return 8
                else:
                    self.weight_arrangement = 0
                    self.weight_arrangement_part = 0
        except:
            return

    def check_generate_cards(self, cards_2d):
        # Generowanie 5 kart oraz sprawdzanie jaki to uklad
            
        for idx1 in range(0, len(cards_2d)):
            for idx2 in range(0, len(cards_2d[idx1])):
                self.cards.append(cards_2d[idx1][idx2])
                # W tablicy kart przypisz uklad kart do nowej tablicy do czwartej karty
                if idx2 % 4 == 0 and idx2 > 0 and idx2 < 5:
                    self.cards_5 = self.cards[:]

                # for idx3 in range(0, len(self.cards_5)):
                #     self.cards_5[idx3].print()

                if idx2 > 3:
                    self.cards_5.pop()
                    self.cards_5.append(cards_2d[idx1][idx2])

                    self.perm = self.cards_5
                    
                    if self.if_combs:
                        for idx7 in range(0, len(self.perm)):
                            if self.random == False:
                                self.file.write(self.perm[idx7].print_str() + " ")
                                # self.perm[idx7].print()
                        if self.random == False:
                            self.file.write("\n")
                            # print()

                        self.loading_bar_combs.update_progress(self.num_arr)
                    
                        if not self.loading_bar_combs.check_stop_event():
                            sys.exit()
                        
                        self.helper_arr.append_cards_all_permutations(self.perm)

                        self.c_idx6 = 0
                        self.arrangement_recogn(self.perm)

                        self.helper_arr.clear_indices_2d_1()
                    
                    self.combs = list(itertools.permutations(self.perm))

                    # for idx7 in range(0, len(self.combs)):
                    #     for idx8 in range(0, len(self.combs[idx7])):
                    #         self.combs[idx7][idx8].print()
                    #     print()
                    
                    self.cards_perm = []

                    self.cards_perm = set(self.combs)
                    self.cards_perm = [list(i) for i in self.cards_perm]

                    if not self.if_combs:
                        for idx6 in range(0, len(self.cards_perm)):
                            if self.random == False:
                                for idx7 in range(0, len(self.cards_perm[idx6])):
                                    # self.cards_perm[idx6][idx7].print()
                                    self.file.write(self.cards_perm[idx6][idx7].print_str() + " ")
                                # print()
                                self.file.write("\n")
                            

                            self.loading_bar.update_progress(self.num_arr)
                            
                            if not self.loading_bar.check_stop_event():
                                sys.exit()
                            self.helper_arr.append_cards_all_permutations(self.cards_perm[idx6])

                            self.c_idx6 = idx6
                            self.arrangement_recogn()

                            self.helper_arr.clear_indices_2d_1()

            self.cards = []

        self.helper_arr.check_if_weights_larger()
        
        self.file.close()

        return self.helper_arr.random_arrangement()

    def carriage_generating(self, random, if_combs):
        #Zmienna uzywana do okreslenia czy uklad bedzie losowany
        self.random = random
        self.if_combs = if_combs
        
        if self.if_combs:        
            redis_buffer_instance.redis_1.set('min', '0')
            redis_buffer_instance.redis_1.set('max', self.max_combs)
        else:
            redis_buffer_instance.redis_1.set('min', '0')
            redis_buffer_instance.redis_1.set('max', self.max_1)
            
        shift = 0

        #Iterowanie po figurach
        for i in range(0, len(self.cardmarkings.arrangements)):
            self.cards_1d = []
            #Iterowanie po kolorach
            for color in self.cardmarkings.colors:
                #Zapisanie do tablicy karty (figura i kolor)
                self.cards_1d.append(Card(self.cardmarkings.arrangements[i], color))
                #Ostatni kolor
                if color == 'Ka':
                    #To zapisanie 4 pierwszych figur o roznych kolorach
                    self.cards_2d.append(self.cards_1d)
                    #Zapisanie reszty kart
                    for color in range(0, len(self.cardmarkings.colors)):
                        for m in range(0, len(self.cardmarkings.arrangements)):
                            self.cards_1d.append(Card(self.cardmarkings.arrangements[m], self.cardmarkings.colors[color]))
                    #Usuwanie powtarzajacych sie kart w kolejnych partiach kart
                    z = 0
                    for idx in range(0, 3):
                        self.cards_1d.pop(17 + z + shift)
                        z += 12
                    #Usuwanie takiej samej karty jaka jest w ukladzie kareta np. 4 4 4 4  pop(4)
                    self.cards_1d.pop(4+shift)
                    #Zmienna pomocnicza poniewaz taka sama karta przesuwa sie co n indeksow
                    shift += 1

        #Ostateczna forma np.
        # 2Ki 2Tr 2Pi 2Ka 3Ki 4Ki ... AKi 3Tr 4Tr ... ATr 3Pi 4Pi ... APi 3Ka 4Ka ... AKa

        # for idx1 in range(0, len(self.cards_2d)):
        #     for idx2 in range(0, len(self.cards_2d[idx1])):
        #         self.cards_2d[idx1][idx2].print()
        #     print()

        return self.check_generate_cards(self.cards_2d)


