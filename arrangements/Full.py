from classes.Card import Card
from arrangements.HelperArrangement import HelperArrangement
from arrangements.LoadingBar import LoadingBar
from arrangements.CardMarkings import CardMarkings
from itertools import chain
import itertools

class Full(HelperArrangement):
    
    def __init__(self):
        self.cardmarkings:CardMarkings = CardMarkings()   #Oznaczenia kart
        self.loading_bar:LoadingBar = LoadingBar(449279, 40, 39)
        self.file = open("permutations_data/full.txt", 'w')
        
        self.cards:list = []                      #Tablica na karty
        self.cards_2d:list = []                   #Tablica do przetwarzania ukladow
        self.cards_1d:list = []                   #Tablica do przetwarzania ukladow
        self.cards_1d_comb:list = []              #Tablica do przetwarzania ukladow kombinacje
        self.cards_2d_5:list = []                 #Tablica do wyswietlania (testy)
        self.perm:list = []

        self.num_arr:int = 0                     #Liczenie ukladow kart w kolejnych iteracjach
        self.c_idx6:int  = 0
        self.rand_int:int  = 0

        self.if_perm_weights:bool = True
        self.random:bool = False                  #Jesli jest losowanie ukladu
        self.example:bool = False                 #Jesli jest recznie wpisany uklad
        self.print_permutations:bool = True       #Czy wyswietlic wszystkie permutacje
    
    #tabnine: document
    def set_cards(self, cards):
        self.perm = cards
        self.random = True
        self.example = True
    
    def set_rand_int(self, rand_int):
        self.rand_int = rand_int

    def get_weight(self):
        if self.weight_arrangement > 0:
            return self.weight_arrangement
        
    def get_part_weight(self):
        return 0

    def print_arrengement(self):
        if self.random == False:
            print("Full: ", self.weight_arrangement, "Numer: ", self.num_arr)
        if self.random == True:
            print("Full: ", self.weight_arrangement, "Numer: ", self.rand_int)

    def remove_repeats_full(self):
        #Usuwanie tych samych kart ktorych liczba jest rowna 4
        for i in range(0, len(HelperArrangement().get_indices_2d_1())):
            if (len(HelperArrangement().get_indices_2d_1()[i]) == 4):  # Jesli w wierszu tablicy znajduja sie 4 elementy
                return True
        return False

    def arrangement_recogn(self):
        # Sprawdzanie czy uklad kart to full oraz przypisanie wagi do ukladu
        self.if_full = 0  # Sumowanie tych samych kart
        weight_1 = 0
        weight_2 = 0
        indices_1 = False
        indices_2 = False

        self.weight_arrangement = 0

        if self.example == True:
            if len(HelperArrangement().dim(self.perm)) == 2:
                self.perm = list(chain.from_iterable(self.perm))

            HelperArrangement().get_indices_1(self.perm)

            self.c_idx6 = 0
            self.perm = [self.perm]

        for i in range(0, len(HelperArrangement().get_indices_2d_1())):
            #print("Rozmiar: ", len(self.indices_2d[i]))
            if ((len(HelperArrangement().get_indices_2d_1()[i]) == 3) and indices_1 == False):  # Jesli w wierszu tablicy znajduja sie 3 elementy
                for j in range(0, len(HelperArrangement().get_indices_2d_1()[i])):
                    weight_1 += pow(self.perm[self.c_idx6][HelperArrangement().get_indices_2d_1()[i][j]].weight, 3)
                    #print(weight_1)
                    indices_1 = True
                self.if_full += 1
            if ((len(HelperArrangement().get_indices_2d_1()[i]) == 2) and indices_2 == False):  # Jesli w wierszu tablicy znajduja sie 2 elementy
                for k in range(0, len(HelperArrangement().get_indices_2d_1()[i])):
                    weight_2 += self.perm[self.c_idx6][HelperArrangement().get_indices_2d_1()[i][k]].weight * 2
                    #print(weight_2)
                    indices_2 = True
                self.if_full += 1
        if (self.if_full == 2):
            self.weight_arrangement = (weight_1 + weight_2) + 12408806
            HelperArrangement().append_weight_gen(self.weight_arrangement)  # Tablica wag dla sprawdzania czy wygenerowane uklady maja wieksze
            if self.random == False:
                self.file.write("Full: " + str(self.weight_arrangement) + " Numer: " + str(self.num_arr) + "\n")
                
            self.num_arr += 1
                
            if self.example == True:                
                self.print_arrengement()
                
                for idx in range(0, len(self.perm[self.c_idx6])):
                    with open("permutations_data/full.txt", 'a') as file:
                        file.write(self.perm[self.c_idx6][idx].print_str() + " ")
                with open("permutations_data/full.txt", 'a') as file:
                    file.write("\n")
                    
                with open("permutations_data/full.txt", 'a') as file:
                    file.write("Full: " + str(self.weight_arrangement) + " Numer: " + str(self.rand_int) + "\n")
                
            return 7

    def full_generating(self, random):
        self.cards_2d = []
        self.random = random

        for i in self.cardmarkings.arrangements:        #Iteracja po oznaczeniach
            self.cards_1d = []
            for idx1 in range(0, 4):                    #Dodanie 4 pierwszych kart
                self.cards_1d.append(Card(i, self.cardmarkings.colors[idx1]))   #

            self.cards_1d_comb = list(itertools.combinations(self.cards_1d, 4))

            #Iteracja po tablicy z kombinacjami
            for idx2 in self.cards_1d_comb:
                self.cards_1d = []
                #Dazenie do tablicy postaci AKi ATr APi 2Ki 3Ki 4Ki 5Ki 6Ki ...
                for idx3 in range(0, len(idx2)):
                    self.cards_1d.append(Card(idx2[idx3].name, idx2[idx3].color))
                    if idx3 == 2:
                        for idx4 in self.cardmarkings.colors:
                            for idx5 in range(0, len(self.cardmarkings.arrangements)):
                                self.cards_1d.append(Card(self.cardmarkings.arrangements[idx5], idx4))
                        self.cards_2d.append(self.cards_1d)

        #Tablica ma byc postaci AKi ATr APi 2Ki 3Ki 4Ki 5Ki 6Ki ... QKi KKi AKi 2Tr 3Tr 4Tr ... KTr ATr
        # for idx6 in range(0, len(self.cards_2d)):
        #     for idx7 in range(0, len(self.cards_2d[idx6])):
        #         self.cards_2d[idx6][idx7].print()
        #     print()

        #Filtracja kart o takich samych kolorach
        #Przed: 2Ki 2Tr 2Pi 2Ki 3Ki ... KKi AKi 2Tr 3Tr ...
        #Po: 2Ki 2Tr 2Pi 3Ki ... KKi AKi 3Tr 4Tr ...
        shift1 = 0
        shift2 = 12
        shift3 = 24
        shift4 = 36
        for idx1 in range(0, len(self.cards_2d)):
            self.cards_2d[idx1].pop(3 + shift1)
            self.cards_2d[idx1].pop(3 + shift2)
            self.cards_2d[idx1].pop(3 + shift3)
            self.cards_2d[idx1].pop(3 + shift4)
            if ((idx1 + 1) % 1 == 0):
                shift1 += 1
                shift2 += 1
                shift3 += 1
                shift4 += 1

        shift5 = 1
        shift6 = 0

        # for idx11 in range(0, len(self.cards_1d)):
        #     self.cards_1d[idx11].print()

        #Sortowanie do postaci: 2Ki 2Tr 2Pi 2Ka 3Ki 3Tr 3Pi 3Ka 4Ki 4Tr 4Pi ...
        for idx1 in range(0, len(self.cards_2d)):
            self.cards_2d[idx1].sort()

        # for idx6 in range(0, len(self.cards_2d)):
        #     for idx7 in range(0, len(self.cards_2d[idx6])):
        #         self.cards_2d[idx6][idx7].print()
        #     print()

        for idx1 in range(0, len(self.cards_2d)):
            for idx2 in range(0, len(self.cards_2d[idx1])):
                if idx2 == 8:
                    for idx6 in range(0, len(self.cards_2d[idx1])):
                        if idx2 == len(self.cards_2d[idx1]):
                            shift6 += 1
                        #Usuwanie powtorek np. 2Ki 2Tr 2Pi 2Ki 3Ki ... AKi 2Tr 3Tr ... ATr
                        if (idx1 > 4) and (idx2 > 4 + shift6) and (idx2 < 7 + shift6):
                            self.cards_2d[idx1].insert(0, self.cards_2d[idx1].pop(idx2))
                            shift5 += 1
                        if ((idx1 + 1) % 4 == 0) and (idx1 != 0) and (idx1 > 4):
                            shift6 += 4

        # for idx6 in range(0, len(self.cards_2d)):
        #     for idx7 in range(0, len(self.cards_2d[idx6])):
        #         self.cards_2d[idx6][idx7].print()
        #     print()

        step = 0
        step2 = 0
        step3 = 0

        for idx in range(0, 13):
            for idx1 in range(0, len(self.cards_2d)):

                cards_2d_temp = []
                cards_2d_6 = []

                for idx2 in range(0, len(self.cards_2d[idx1])):
                    if (idx2 >= step2) and (idx2 < 4 + step2):
                        cards_2d_temp.append(self.cards_2d[idx1][idx2])

                    if (idx2 > 3 + step + step3 and idx2 < 8 + step + step3):
                        cards_2d_temp.append(self.cards_2d[idx1][idx2])

                    #Filtracja kart do postaci 2Ki 2Tr 2Pi 2Ka 3Ki 3Tr 3Pi 3Ka w celu utworzenia tablicy kombinacji kart
                    if idx2 == 7 + step + step3:
                        cards_2d_6.append(cards_2d_temp)
                        # print("#######################################")
                        # for idx3 in range(0, len(cards_2d_6)):
                        #     pass
                        #     for idx33 in range(0, len(cards_2d_6[idx3])):
                        #         cards_2d_6[idx3][idx33].print()
                        #     print()

                        self.cards_2d_5.clear()

                        for idx3 in range(0, len(cards_2d_6)):
                            #Utworzenie tablicy z kombinacjami kart (48 * 78 = 3744 kombinacji kart po przetwarzaniu)
                            self.cards_2d_5.append(list(itertools.combinations(cards_2d_6[idx3], 5)))

                            self.cards_2d_5 = list(chain.from_iterable(self.cards_2d_5))
                            self.cards_2d_5 = [list(i) for i in self.cards_2d_5]

                        for idx5 in range(0, len(self.cards_2d_5)):
                            #print(self.cards_2d_5[idx5])

                            # Pobranie indeksow z tablicy permutacji w ktorych wystepuje FULL np. [1, 3, 4][2, 5]
                            HelperArrangement().get_indices_1(self.cards_2d_5[idx5])

                            # Usuwanie liczby kart wiekszych od 3
                            if_remove = self.remove_repeats_full()

                            if if_remove == True:
                                self.cards_2d_5[idx5].clear()

                            HelperArrangement().clear_indices_2d_1()

                            self.cards_2d_5[idx5] = [ele for ele in self.cards_2d_5[idx5] if ele != []]

                            # for idx55 in range(0, len(self.cards_2d_5)):
                            #     for idx66 in range(0, len(self.cards_2d_5[idx55])):
                            #         self.cards_2d_5[idx55][idx66].print()
                            #     print()

                            self.perm = list(itertools.permutations(self.cards_2d_5[idx5], 5))
                            self.file = open("permutations_data/full.txt", "a")
                            for idx6 in range(0, len(self.perm)):
                                HelperArrangement().get_indices_1(self.perm[idx6])

                                if self.random == False:
                                    for idx7 in range(0, len(self.perm[idx6])):
                                        #self.perm[idx6][idx7].print()
                                        # with open("permutations_data/full.txt", "a") as f:
                                        self.file.write(self.perm[idx6][idx7].print_str() + " ")
                                    #print()
                                    # with open("permutations_data/full.txt", "a") as f:
                                    self.file.write("\n")
            
                                self.loading_bar.set_count_bar(self.num_arr)
                                self.loading_bar.display_bar()

                                self.c_idx6 = idx6
                                self.arrangement_recogn()

                                HelperArrangement().clear_indices_2d_1()

                                # Tablica permutacji do wylosowania ukladu
                                HelperArrangement().append_cards_all_permutations(self.perm[idx6])

                step += 4

            step = 0
            step2 += 4
            step3 += 4

        HelperArrangement().check_if_weights_larger()
        
        self.file.close()
        
        return HelperArrangement().random_arrangement()
