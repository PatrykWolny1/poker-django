from classes.Card import Card
from arrangements.HelperArrangement import HelperArrangement
from arrangements.LoadingBar import LoadingBar
from arrangements.CardMarkings import CardMarkings
from itertools import permutations, combinations

class TwoPairs(HelperArrangement):
    
    def __init__(self):
        self.cardmarkings:CardMarkings = CardMarkings()  # Oznaczenia kart
        self.limit_rand:int = 2                 # Ograniczenie dla liczby obliczen 143 - pelne obliczenie
        self.one_iter:int = 103680
        self.loading_bar:LoadingBar = LoadingBar(self.one_iter * self.limit_rand - 1, 40, 54)   #14826239
        self.high_card:Card = Card()             # Wysoka karta
        self.file = open("permutations_data/two_pairs.txt", "w")

        self.cards_2d:list = []                  # Przygotowanie listy pod kombinacje i permutacje
        self.cards_2d_acc:list = []              # Lista pomocnicza
        self.cards_begin:list = []               # Lista pomocnicza
        self.cards_comb:list = []                # Lista na kombinacje
        self.perm:list = []                      # Lista na permutacje

        self.c_idx1:int = 0
        self.two_pairs_sum:int = 0              # Suma wag
        self.two_pairs_part_sum:int = 0         # Waga wysokiej karty
        self.count:int = 0                      # Licznik do funkcji temp_lambda()
        self.count_bar:int = 0                  # Licznik do obiektu LoadingBar
        self.num_arr:int = 0                    # Licznik ukladow
        self.idx_high_c:int = 0                 # Zmienna pomocnicza do dodania kolumny z wysoka karta
        self.rand_iter:int = 0                  # Ile iteracji zostalo wykonanych w celu ograniczenia liczby obliczen

        self.random:bool = False
        self.example:bool = False

    def set_cards(self, cards):
        self.perm = cards
        self.example = True
        self.random = True

    def set_rand_int(self, rand_int):
        self.rand_int = rand_int
        
    def get_weight(self):
        if self.two_pairs_sum > 0:
            return self.two_pairs_sum

    def get_part_weight(self):
        if self.two_pairs_part_sum > 0:
            return [self.two_pairs_part_sum]

    def print_arrengement(self):
        if self.random == False:
            print("Dwie pary:", self.two_pairs_sum, "Wysoka Karta:", self.high_card.print_str(), "Numer:", self.num_arr)
        if self.random == True:
            print("Dwie pary:", self.two_pairs_sum, "Wysoka Karta:", self.high_card.print_str(), "Numer:", self.rand_int)

    def filter_func(self, list_comb):
        #Filtruje liste o permutacje ktore nie sa dwiema parami

        count = 0

        for idx in range(0, len(HelperArrangement().get_indices_2d_1())):
            #Jesli wiecej niz 2 takie same karty to zwroc falsz
            if len(HelperArrangement().get_indices_2d_1()[idx]) > 2:
                count += 1
        if count > 0:
            return False
        else:
            return True

    # def moving_average(a, n=3):
    #     ret = np.cumsum(a, dtype=float)
    #     ret[n:] = ret[n:] - ret[:-n]
    #     return ret[n - 1:] / n

    def temp_lambda(self, t1):
        # Jesli koniec sekwencji wag i sumy [[Card int] [Card int] ... [Card int] sum][[Card int] ... [Card int] sum]
        if self.count == 7:
            self.count = 0
            return

        self.count += 1

        # Zamiana indeksu kart (LISTA!) na string (SAMA LICZBA) (czyli self.count < 6, gdzie poczatek self.count zaczyna sie od 1)
        if self.count < 6:
            t2 = ''.join(map(str, t1[1]))
            if int(t2) < 5:
                return t1[1]
        # Zamiana wagi calego ukladu na string (bez listy)
        elif self.count == 6:
            # t3 = ''.join(map(str, t1))
            # if int(t3) > 4:
            return t1

    def arrangement_recogn(self):
        count_one_pair = 0      # Zmienna potrzebna do okreslenie czy jest to para
        count_two_pairs = 0     # Zmienna okreslajaca czy sa to dwie pary
        c_two_pairs = False     # Zmienna tymczasowa (pomocnicza)
        pow_two_pairs = 3       # Potega dla jednej i drugiej pary [4 6]
        self.two_pairs_sum = 0  # Zmienna zawierajaca sume wag tymczasowych

        if self.example == True:
            self.c_idx1 = 0
            
            if len(HelperArrangement().dim(self.perm)) == 1:
                self.perm = [self.perm]
            
        HelperArrangement().clear_indices_2d_1()    
        #print(self.perm[self.c_idx1])
        HelperArrangement().get_indices_1(sorted(self.perm[self.c_idx1]))

        # Okreslenie czy uklad to dwie pary
        for idx in range(0, len(HelperArrangement().get_indices_2d_1())):
            # Jesli wystepuje 1 karta to jest to wysoka karta
            if len(HelperArrangement().get_indices_2d_1()[idx]) == 1:
                high_card_idx = int(''.join(str(i) for i in HelperArrangement().get_indices_2d_1()[idx]))

                #Przypisanie wysokiej karty z posortowanej tablicy
                self.high_card = sorted(self.perm[self.c_idx1])[high_card_idx]

                two_pairs_weight = pow(sorted(self.perm[self.c_idx1])[high_card_idx].weight, 2)

                # Sumowanie tymczasowej wagi wysokiej karty
                self.two_pairs_sum += two_pairs_weight

                self.two_pairs_part_sum = sorted(self.perm[self.c_idx1])[high_card_idx].weight

            # Jesli wystepuja dwie takie same karty to jest to para
            if len(HelperArrangement().get_indices_2d_1()[idx]) == 2:
                # Dla pierwszej iteracji (jednej pary) count_two_pairs != 0
                if c_two_pairs == True:
                    c_two_pairs = False
                    count_one_pair = 0
                count_one_pair += 1
                count_two_pairs += 1

                # Jesli jedna para z tablicy HelperArrangement().get_indices_2d_1() czyli [1, 1][1, 1]
                if count_one_pair == 2:
                    two_pairs_weight = pow(sorted(self.perm[self.c_idx1])[HelperArrangement().get_indices_2d_1()[idx][0]].weight,
                                           pow_two_pairs)
                    self.two_pairs_sum += two_pairs_weight
                    two_pairs_weight = pow(sorted(self.perm[self.c_idx1])[HelperArrangement().get_indices_2d_1()[idx][1]].weight,
                                           pow_two_pairs)
                    self.two_pairs_sum += two_pairs_weight

                    #print(self.two_pairs_sum)

                    # Zwiekszenie potegi do 6 dla nastepnej pary (wyzszej)
                    pow_two_pairs = 4

                    # Pierwsza iteracja zakonczona
                    c_two_pairs = True
                #print()

            # Jesli nie sa to dwie pary to zwroc Prawda i wyzeruj sume
            if len(HelperArrangement().get_indices_2d_1()[idx]) == 3:
                self.two_pairs_sum = 0
                return None

        self.two_pairs_sum += 10065826
        HelperArrangement().append_weight_gen(self.two_pairs_sum)

        if self.random == False and count_two_pairs == 4:
            self.file.write("Dwie pary: " + str(self.two_pairs_sum) +
                            " Wysoka Karta: " + self.high_card.print_str() +
                            " Numer: " + str(self.num_arr) + "\n")
            self.num_arr += 1
            #self.print_arrengement()

        if self.example == True and count_two_pairs == 4:
            self.print_arrengement()
            
            for idx in range(0, len(self.perm[self.c_idx1])):
                with open("permutations_data/two_pairs.txt", "a") as file:
                    file.write(self.perm[self.c_idx1][idx].print_str() + " ")
                    
            with open("permutations_data/two_pairs.txt", "a") as file:
                file.write("\n")
            
            with open("permutations_data/two_pairs.txt", "a") as file:
                file.write("Dwie pary: " + str(self.two_pairs_sum) + 
                           " Wysoka Karta: " + self.high_card.print_str() + " " +
                           " Numer: " + str(self.rand_int) + "\n")
            
            return 3
        else:
            self.two_pairs_sum = 0
            self.two_pairs_part_sum = 0

        # Zmienna do funkcji temp_lambda
        self.count = 0

        HelperArrangement().clear_indices_2d_1()

    def combinations_generating(self):
        self.cards_comb = list(combinations(self.cards_begin, 5))

        self.cards_comb = [list(i) for i in self.cards_comb]

        for idx in range(0, len(self.cards_comb)):
            HelperArrangement().get_indices_1(self.cards_comb[idx])

            # Filtrowanie listy z niepotrzebnych ukladow kart
            self.cards_comb[idx] = list(filter(self.filter_func, self.cards_comb[idx])).copy()

            HelperArrangement().clear_indices_2d_1()

            self.perm = list(permutations(self.cards_comb[idx], 5))
            self.perm = [list(j) for j in self.perm]

            for idx1 in range(0, len(self.perm)):
                self.loading_bar.set_count_bar(self.count_bar)
                self.loading_bar.display_bar()
                self.count_bar += 1

                if self.random == False:
                    for idx2 in range(0, len(self.perm[idx1])):
                        #self.perm[idx1][idx2].print()
                        self.file.write(self.perm[idx1][idx2].print_str() + " ")
                    #print()
                    self.file.write("\n")
                
                self.c_idx1 = idx1
                
                if_not_two_pairs = self.arrangement_recogn()
                if if_not_two_pairs:
                    return None
                
                HelperArrangement().clear_indices_2d_1()

                HelperArrangement().append_cards_all_permutations(self.perm[idx1])
        
        if self.rand_iter == self.limit_rand:
            HelperArrangement().check_if_weights_larger(False)

            return HelperArrangement().random_arrangement()
        
        self.rand_iter += 1

        self.file.write("Numer iteracji: " + str(self.rand_iter) + "\n")

        self.perm.clear()
        self.cards_comb.clear()

    def two_pairs_generating(self, random):
        self.random = random

        self.cards_2d = []

        p = True
        q = False
        z = False

        idx = 0  # Do figur kart
        idx2 = 0  # While
        idx4 = 0  # Do pierwszych 8 kart
        limit_1 = 8  # Zakres kart w odniesieniu do calej talii
        limit_2 = 12
        count_1 = 0  # Pomocnicza do pierwszych 8 kart
        count_2 = 0  # Do iterowania zwieksza sie
        iter_count_2 = 11  # zmniejsza sie
        step = 0  # Krok do zakresu kart (limit_1 i limit_2)
        count_11 = 0  # Pomocnicza,
        count_all = 0  # Zwiekszana co iteracje do wyboru kart od danego ukladu 4 kart
        count_all_1 = 1  # Liczy uklady
        iter_count_1 = 12  # Zmienna okreslajaca ilosc figur uzytych w algorytmie (iteracje)
        iter_count_11 = 13  # Zmienna okreslajaca ilosc figur uzytych w algorytmie oznaczajaca
        # uklad znajdujacy sie o jedna iterecje nizej od iter_count_1
        i = 0  # Zmienna pomocnicza, inkrementowana do figur kart (idx)
        j = 0  # Zmienna pomocnicza, dekrementowana
        k = 9  # Zmienna okreslajaca koniec sprawdzanych ukladow
        x = False  # Zmienna uzywana do powtorzenia danej iteracji
        y = False  # Zmienna uzywana do powtorzenia danej iteracji
        l = 0  # Do iterowania (oznacza rozmiar ukladow), zwiekszana
        l_1 = -2  # Zmienna pomocnicza, zmniejszana

        while (p):
            m = len(self.cardmarkings.colors)
            while idx2 < m:
                # Dodawanie kart idx zwiekszany z kazda iteracja po to by nie powtarzaly sie karty
                self.cards_2d.append(Card(self.cardmarkings.arrangements[idx], self.cardmarkings.colors[idx2]))
                idx2 += 1
                idx4 += 1
                # Jesli dodawanie wszystkich 4 kolorow zakonczone
                if idx2 == 4:
                    idx += 1
                    idx2 = 0
                    count_1 += 1

                # Dodaje poczatek ukladu kart np. 2Ki 2Tr 2Pi 2Ka 3Ki 3Tr 3Pi 3Ka  || 3Ki 3Tr 3Pi 3Ka 4Ki 4Tr 4Pi 4Ka
                if count_1 == 2 and idx4 == 8:
                    self.cards_begin = self.cards_2d.copy()
                    # for idx11 in range(0, len(self.cards_begin)):
                    #     self.cards_begin[idx11].print()
                    # print()
                # Dodaje karty co 4 iteracje na poczatek sekwencji np. 2Ki 2Tr 2Pi 2Ka ... 4Ki 4Tr 4Pi 4Ka 5Ki 5Tr ... || ... 3Ki 3Tr ... 7Ki 7Tr 7Pi 7Ka ...
                if (((count_all + 1) % 8) == 0) or count_1 == 13 - count_11:
                    for idx11 in range(0, len(self.cards_2d)):
                        # self.cards_2d[idx11].print()
                        self.cards_2d_acc.append(self.cards_2d[idx11])
                    self.cards_2d = []

                    # for idx11 in range(0, len(self.cards_2d_acc)):
                    #     self.cards_2d_acc[idx11].print()
                    # print()
                    # print("COUNT_1", count_11)

                    if count_11 == 11:
                        self.check_if_weights_larger(False)
                                                
                        return self.random_arrangement()

                    # Jesli jest ostatnia karta to zacznij operacje A ... K ... Q ... J ... 10 ...
                    if count_1 == 13 - count_11:

                        # print()
                        # print()
                        # print("------------------------------------------------------------------")
                        # print("##################################################################")
                        # print("------------------------------------------------------------------")

                        while (True):

                            # for idx11 in range(0, len(self.cards_2d_acc)):
                            #     self.cards_2d_acc[idx11].print()

                            # print()
                            # print()

                            # print()

                            # for idx11 in range(0, len(self.cards_begin)):
                            #     self.cards_begin[idx11].print()
                            # print()

                            # for idx11 in range(0, len(self.cards_2d_acc)):
                            #     self.cards_2d_acc[idx11].print()
                            # print()

                            # print("count_all_1: ", count_all_1)

                            # Dla 1 karty omin zwiekszanie limitow
                            if count_all_1 == 1:
                                pass
                            else:
                                limit_1 += 4
                                limit_2 += 4

                            # Jesli zmiana iteracji sekwencji np. 2Ki 2Tr 2Pi 2Ka (1) ... AKi ATr APi AKa || 3Ki 3Tr 3Pi 3Ka (67) ... 4Ka 5Ki 5Tr 5Pi 5Ka
                            if count_all_1 in [67, 122, 167, 203, 231, 251, 267, 277]:
                                iter_count_1 += 1

                            # Zwieksz limit o krok jesli zmiana iteracji sekwencji (poziom nizej od powyzszej)(zbior)
                            if count_all_1 == iter_count_11 and z == True:
                                #print("------------------------------------------")
                                limit_1 = 8 + step
                                limit_2 = 16 + step

                            # Zmien limit
                            if count_all_1 == iter_count_1 and z == True:
                                limit_1 = limit_2 - 4

                            # Dla pierwszej iteracji nie zmieniaj kroku
                            if q:
                                step += 4
                                q = False

                            # Algorytm dla ustalenia wartosci iter_count_1 oraz iter_count_11
                            if (count_all_1 == iter_count_1 and z == True):
                                # iter_count_11 jest zawsze mniejszy o 1 od iter_count_1
                                iter_count_11 = iter_count_1 - 1

                                # print("##########################################")
                                # print("iter_COUNT_1: ", iter_count_1)
                                # print("J: ", j)
                                # print("K-1: ", k - 1)
                                # print("L: ", l)
                                if iter_count_11 in [67, 122, 168, 203]:
                                    pass
                                else:
                                    pass
                                    # print("iter_COUNT_11: ", iter_count_11)
                                    # print("##########################################")

                                if l in [2, 3]:
                                    iter_count_1 -= 1
                                if l in [4, 5, 6, 7, 8, 9]:
                                    iter_count_1 -= l_1

                                iter_count_1 += 10 - j

                                if j == k - 1:
                                    if x == True:
                                        k -= 1
                                    x = True
                                    j = 0

                                    if l in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
                                        y = False

                                    l += 1
                                    l_1 += 1

                                    if l in [2, 4, 5, 6, 7, 8, 9]:
                                        iter_count_11 -= 1
                                    if l == 3:
                                        iter_count_1 += 1

                                j += 1

                                if j == 1 and (k - 1) in [8, 7, 6, 5, 4, 3, 2, 1, 0] and y == False:
                                    j = 0
                                    y = True

                                iter_count_11 = iter_count_1 - 1

                                if l in [3, 4, 5, 6, 7, 8, 9]:
                                    iter_count_11 -= 1
                                    iter_count_1 -= 1

                            # Dla pierszej iteracji
                            if count_all_1 == 12 and z == False:
                                # print("##########################################")
                                # print("iter_COUNT_1: ", iter_count_1)
                                # print("J: ", j)
                                # print("K-1: ", k - 1)
                                # print("L: ", l)
                                # print("iter_COUNT_11: ", iter_count_11)
                                # print("##########################################")

                                limit_1 = 8
                                limit_2 = 16
                                iter_count_1 += 1
                            # Dla pierwszej iteracji
                            if count_all_1 == 13 and z == False:
                                # print("##########################################")
                                # print("iter_COUNT_1: ", iter_count_1)
                                # print("J: ", j)
                                # print("K-1: ", k - 1)
                                # print("L: ", l)
                                # print("iter_COUNT_11: ", iter_count_11)
                                # print("##########################################")

                                limit_1 = limit_2 - 4
                                iter_count_1 += 10
                                j += 1
                                z = True
                                iter_count_11 = iter_count_1 - 1

                            # Dla limitu powyzej liczby kart
                            if limit_1 == 52:
                                limit_1 = 12
                                limit_2 = 20

                            # Na podstawie wyliczonego limitu dodaj karty z tablicy o okreslonej liczbie kart
                            for idx11 in range(limit_1, limit_2):
                                self.cards_begin.append(self.cards_2d_acc[idx11])

                            # print("limit1: ", limit_1)
                            # print("limit2: ", limit_2)
                            # for idx11 in range(0, len(self.cards_begin)):
                            #     self.cards_begin[idx11].print()
                            # print()

                            #####################################TUTAJ UMIESCIC RESZTE
                            cards = self.combinations_generating()
                            if cards:
                                self.file.close()
                                return cards

                            for idx11 in range(0, 4):
                                self.cards_begin.pop()

                            # for idx11 in range(0, len(self.cards_begin)):
                            #     self.cards_begin[idx11].print()
                            # print()

                            count_1 += 1
                            count_2 += 1

                            count_all_1 += 1

                            # Kolejna iteracja
                            if count_2 == iter_count_2:
                                # Usun karty z tablicy zeby dodac nastepne
                                for idx11 in range(0, 4):
                                    self.cards_begin.pop()
                                iter_count_2 -= 1
                                count_2 = 0
                                q = True

                                # for idx11 in range(0, len(self.cards_begin)):
                                #     self.cards_begin[idx11].print()
                                # print()

                                # Nowa iteracja (nastepna)
                                if iter_count_2 == 0:
                                    self.count_bar = 0
                                    q = False
                                    step = 0
                                    iter_count_2 = 10 - i
                                    i += 1
                                    idx = i
                                    idx2 = 0
                                    idx4 = 0
                                    count_1 = 0
                                    count_11 += 1
                                    count_all = -1
                                    limit_1 = 4
                                    limit_2 = 8
                                    self.cards_begin.clear()
                                    self.cards_2d_acc.clear()
                                    break
                                else:
                                    continue
                count_all += 1

