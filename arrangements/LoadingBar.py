from django.core.cache import cache
from numpy import floor
from home.redis_buffer_singleton import redis_buffer_instance_stop
import time
import shutil

class LoadingBar(object):

    def __init__(self, n_bar, points_step, points_finished, helper_arr):
        self.step_p:bool = True
        self.str_1:str = ""
        self.n_bar:int = n_bar                                          # Ilosc ukladow (trzeba uruchomic program i policzyc)
        self.step_bar:int = int(self.n_bar / points_step)               # Ilosc punktow ladowania (40 - dzielnik)
        self.step_bar_finished:int = int(self.n_bar / points_finished)  # Ilosc zaladowanych punktow (co jeden) [.####][..###]
        self.count_bar:int = 0
        self.progress:int = 0
        self.helper_arr = helper_arr
        self.begin = True
        self.ret_lb = True
        self.points_step = points_step
        
    def set_count_bar(self, count_bar):
        self.count_bar = count_bar

    def display_bar(self):
        from home.views import data_ready_event, stop_event, cache_lock_progress, cache_lock_event_var
        
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
            # os.system('cls')
            self.step_p = False
        # Zamiana znaku "#" na ".", co okreslona liczbe iteracji
        if self.step_p == False and (self.count_bar % self.step_bar_finished) == 0:
            # print("[", end="")
            self.str_1 = self.str_1.replace("#", ".", 1)
            # print(self.str_1, end="]\n")
            with cache_lock_progress:
                cache.set('shared_progress', str(self.str_1.count('.')))
            data_ready_event.set()
            data_ready_event.clear()
            # os.system('cls')
            # time.sleep(0.1)
        # Ostatnia iteracja zamiana znaku
        if self.count_bar == self.n_bar - 1:
            # print("[", end="")
            self.str_1 = self.str_1.replace("#", ".", 1)
            # print(self.str_1, end="]\n")
            with cache_lock_progress:
                cache.set('shared_progress', str(self.str_1.count('.')))
            data_ready_event.set()       
            
        if stop_event.is_set():
            self.ret_lb = False
            with cache_lock_event_var:
                shutil.copyfile(self.helper_arr.helper_file_class.file_path.resolve(), self.helper_arr.helper_file_class.file_path_dst.resolve())
                
                with open(self.helper_arr.helper_file_class.file_path_dst.resolve(), 'r') as file:
                    lines = file.readlines()
                    line_count = len(lines)
                    
                print("Ilosc zapisanych ukladów: ", int(floor(line_count/2)))
                
                self.helper_arr.weight_gen.clear()
                self.helper_arr.cards_all_permutations.clear()
                
                redis_buffer_instance_stop.redis_1.set('stop_event_var', '1')
                return self.ret_lb               
        else:
            if self.begin:
                self.helper_arr.helper_file_class.file_path_dst.write_text('')
                self.begin = False
            return self.ret_lb
