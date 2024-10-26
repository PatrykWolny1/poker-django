from classes.Card import Card
from arrangements.HelperArrangement import HelperArrangement
from arrangements.LoadingBar import LoadingBar
from arrangements.CardMarkings import CardMarkings
from itertools import permutations

class StraightRoyalFlush(HelperArrangement):
    
    def __init__(self):
        self.cardmarkings:CardMarkings = CardMarkings()  #Oznaczenia kart
        self.loading_bar:LoadingBar = LoadingBar(4799, 39, 40)
        self.file = open("permutations_data/straight_royal_flush.txt", "w")
        self.cards:list = []                     #Tablica na karty
        self.perm:list = []                      #Tablica na permutacje do wag

        self.weight_arrangement:int = 0         #Tablica na wage ukladu
        self.num_arr:int = 0                    #Liczenie ukladow kart w kolejnych iteracjach
        self.c_idx2:int = 0
        self.rand_int:int = 0

        self.random:bool = False                 #Jesli jest losowanie ukladu
        self.example:bool = False                #Jesli jest recznie wpisany uklad
        self.if_royal_flush:bool = False         #Jesli jest poker krolewski (prawda) lub poker (falsz)
        self.calc_weights:bool = True            #Zakonczenie petli while oraz identyfikacja czy jest to poker lub poker krolewski

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
        
        HelperArrangement().clear_indices_2d_color()
                
        HelperArrangement().get_indices_color(cards)

        color_5 = False
        for idx in range(0, len(HelperArrangement().get_indices_2d_color())):
            if len(HelperArrangement().get_indices_2d_color()[idx]) == 5:
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
        ace_five = False
        
        if len(HelperArrangement().dim(self.perm)) == 1:
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
        
        HelperArrangement().clear_indices_2d_1()
        HelperArrangement().clear_indices_2d_color()
        
        HelperArrangement().get_indices_color(self.perm[self.c_idx2])
        HelperArrangement().get_indices_1(self.perm[self.c_idx2])
        
        while (self.calc_weights):
            
            # Dla posortowanej tablicy sprawdz czy waga jest mniejsza od kolejnej
            for idx in range(0, len(HelperArrangement().get_indices_2d_1())):
                # Jesli jest 5 takich samych kolorow to powrot z funkcji (poker krolewski)
                if len(HelperArrangement().get_indices_2d_1()[idx]) > 1:
                    return
                if len(HelperArrangement().get_indices_2d_color()[idx]) != 5:
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
                    HelperArrangement().append_weight_gen(self.weight_arrangement)

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

    def straight_royal_flush_generating(self, random):
        self.random = random

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
            temp = []
            for idx2 in range(0, len(cards_2d[idx1])):
                self.cards.append(cards_2d[idx1][idx2])
            temp.append(self.cards)

        # for idx1 in range(0, len(temp)):
        #     for idx2 in range(0, len(temp[idx1])):
        #         temp[idx1][idx2].print()
        #     print()

        # for idx1 in range(0, len(self.perm)):
        #     for idx2 in range(0, len(self.perm[idx1])):
        #         self.perm_temp[idx1][idx2].print()
        #     print()


        #Konwertowanie tymczasowej tablicy do tablicy na permutacje
        for idx1 in range(0, len(temp)):
            for step1, step2 in zip(range(0, len(temp[idx1]), 5), range(5, len(temp[idx1]) + 1, 5)):
            #Generowanie tablicy permutacji
                self.perm = list(permutations(temp[idx1][step1:step2]))

                self.perm = [list(i) for i in self.perm]

                for idx2 in range(0, len(self.perm)):

                    if self.random == False:
                        for idx3 in range(0, len(self.perm[idx2])):
                            #self.perm[idx2][idx3].print()
                            self.file.write(self.perm[idx2][idx3].print_str() + " ")
                        #print()
                        self.file.write("\n")

                    self.c_idx2 = idx2
                    self.arrangement_recogn()

                    HelperArrangement().append_cards_all_permutations(self.perm[idx2])
                    
                    self.loading_bar.set_count_bar(self.num_arr)
                    self.loading_bar.display_bar()        
        
        HelperArrangement().check_if_weights_larger()

        self.file.close()

        return HelperArrangement().random_arrangement()