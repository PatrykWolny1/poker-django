from django.core.cache import cache
from arrangements.HelperArrangement import HelperArrangement
import time
import threading

class LoadingBar(object):

    def __init__(self, n_bar, points_step, points_finished):
        self.step_p:bool = True
        self.str_1:str = ""
        self.n_bar:int = n_bar                                          # Ilosc ukladow (trzeba uruchomic program i policzyc)
        self.step_bar:int = int(self.n_bar / points_step)               # Ilosc punktow ladowania (40 - dzielnik)
        self.step_bar_finished:int = int(self.n_bar / points_finished)  # Ilosc zaladowanych punktow (co jeden) [.####][..###]
        self.count_bar:int = 0
        self.progress:int = 0

    def set_count_bar(self, count_bar):
        self.count_bar = count_bar

    def display_bar(self):
        from home.views import stop_event
        if stop_event.is_set():
            print("Ilosc przetworzonych ukladow: ", len(self.cards_all_permutations))
            HelperArrangement.weight_gen.clear()
            HelperArrangement.cards_all_permutations.clear()
            exit()
        # Pasek postepu
        # Pierwsza wartosc step_p to prawda
        # Tworzony jest pasek postepu stworzony ze znakow "#"
        if self.step_p:
            for i in range(0, self.n_bar, self.step_bar):
                self.str_1 += "#"
        # Tutaj nastepuje wyswietlanie paska ze znakow "#"
        if self.step_p:
            # print("[", end="")
            # print(self.str_1, end="]\n")
            cache.set('shared_variable', str(self.progress))
            self.progress += 1
            # os.system('cls')
            self.step_p = False
            time.sleep(0.1)
        # Zamiana znaku "#" na ".", co okreslona liczbe iteracji
        if self.step_p == False and (self.count_bar % self.step_bar_finished) == 0:
            # print("[", end="")
            self.str_1 = self.str_1.replace("#", ".", 1)
            # print(self.str_1, end="]\n")
            cache.set('shared_variable', str(self.progress))
            self.progress += 1
            # os.system('cls')
            # time.sleep(0.1)
        # Ostatnia iteracja zamiana znaku
        if self.count_bar == self.n_bar - 1:
            # print("[", end="")
            self.str_1 = self.str_1.replace("#", ".", 1)
            # print(self.str_1, end="]\n")
            cache.set('shared_variable', str(self.progress))
            self.progress += 1
            # time.sleep(0.1)
