import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

from classes.Player import Player
from classes.Deck import Deck
from classes.Card import Card
from classes.DataFrameML import DataFrameML
from decision_tree_structure.Node import Node
from decision_tree_structure.OnePairStructureStrategy import OnePairStructureStrategy
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from operator import itemgetter
from random import choice
import numpy as np
import sys
import os
import random
import pandas as pd
import tensorflow as tf
import re
import logging
    
class Croupier(object):

    def __init__(self, game_si_human = 1, all_comb_perm = [], rand_int = 0, game_visible = True, tree_visible = False, prediction_mode = True, n = 1):
        #self.deck:Deck = Deck()
        self.cards:list = []
        self.players:list = []
        self.weights:list = []
        self.all_comb_perm:list = all_comb_perm
        
        self.player:Player = None
        self.X_game:pd.DataFrame = None
        
        #self.rand_int:int = rand_int
        self.game_si_human:int = game_si_human
        self.weight:int = 0
        self.amount:int = 0
        self.idx_players:int = 0
        self.rand_i:int = 0
        self.rand_j:int = 0
        self.n:int = n

        self.exchange:str = ''
        
        self.game_visible:bool = game_visible
        self.tree_visible:bool = tree_visible
        self.prediction_mode:bool = prediction_mode
        
        pd.set_option('display.max_columns', 100)
        
    def clear_data(self):
        self.players.clear()
        self.cards.clear()
        self.weights.clear()
        
        self.weight:int = 0
        self.amount:int = 0
        self.idx_players:int = 0
        self.rand_i:int = 0
        self.rand_j:int = 0
        
    def gather_data(self):
        i = 1
        j = 0
        self.rand_int = random.sample(range(0, len(self.all_comb_perm) - 1), self.n * 2)
        for game in range(0, self.n):
            if game == 0:
                self.rand_i = self.rand_int[game]
                self.rand_j = self.rand_int[game + 1]
            else:
                self.rand_i = self.rand_int[game + j]
                self.rand_j = self.rand_int[game + i]
            
            i += 1
            j += 1
            
            # print(self.rand_int)
            # print(self.rand_i, self.rand_j)
            
            self.random_arrangement()
            self.play()
            self.clear_data()

    
    def play(self):        
        # print()
    
        #self.set_cards()
        
        self.set_players_nicknames()

        
        # for self.player in self.players:
        #     self.player.arrangements.print()
        #     self.player.arrangements.set_rand_int()
        #     self.player.arrangements.check_arrangement(game_visible=self.game_visible)
        
            
        # print()
        
        #########################################################

        # # Dla testowania wybranych uklaldow
        # self.set_cards()
        # player1 = Player(self.deck, cards = self.cards)
        # player1.arrangements.set_cards(self.cards)
        # player1.print()
        # player1.arrangements.check_arrangement(game_visible=self.game_visible)

        #########################################################

        # player1 = Player(deck=self.deck, if_show_perm=True)
        # player1.cards_permutations()

        # # for idx in range(0, len(player1.all_combs)):
        # #     for idx1 in range(0, len(player1.all_combs[idx])):
        # #         player1.all_combs[idx][idx1].print()
        # #     print()

        # player1.arrangements.print()
        # print()
        # player1.arrangements.check_arrangement(game_visible=self.game_visible)

        #########################################################
        #########################################################
        #enablePrint()
        self.weights_cards = []
        
        self.one_pair_strategy = []
        self.num = 0
        self.amount_list = []
        self.exchange_list = []
        
        # Inicjalizacja wag danego ukladu z wylosowanymi kartami, ramek dla danych, pojedynczych wag kart 
        # oprocz tych ktore definuja uklad ([2 2] 3 4 5) dla wybranej strategii, strategii
        for self.player in self.players:
            if self.game_visible == True:
                self.player.print(False) 
                
            self.player.arrangements.check_arrangement(game_visible=self.game_visible)
            self.player.arrangements.set_weights()
            self.player.arrangements.set_data_frame_ml(DataFrameML(nick=self.player.nick, id_arr=self.player.arrangements.get_id(), 
                                                                 weight=self.player.arrangements.get_weight()))
            self.weights_cards.append(self.player.arrangements.get_part_weight())
            
            [self.player.arrangements.data_frame_ml.set_cards_before(card.weight) for card in self.player.cards]
            
            self.one_pair_strategy.append(OnePairStructureStrategy(cards=self.weights_cards[self.num]))
            
            self.num += 1
        
        self.num = 0
        
        # Wyswietlenie drzewa decyzyjnego danej strategii kazdego gracza
        for strategy in self.one_pair_strategy:
            strategy.set_root(visited=False)
            strategy.build_tree()
            
            if self.game_visible == True:
                print(str(strategy.root))

        # Wymiana kart graczy na inne
        self.cards_check_exchange_add_weights()
        
        if self.game_visible == True:
            print()
            print("------------------------------------------------------------")
            print("------------------------------------------------------------")
            print()
        
        # Inicjalizacja wag, ramki danych po wymianie kart
        for self.player in self.players:
            if self.game_visible == True:
                self.player.print(False)
            self.player.arrangements.check_arrangement(game_visible=self.game_visible)
            self.player.arrangements.set_weights()
            self.player.arrangements.data_frame_ml.set_id_arr_after(self.player.arrangements.get_id())

        
        if self.game_visible == True:
            print("Wagi ukladow graczy: ", self.weights)
        
        # Podsumowanie wynikow
        self.compare_players_weights()
        
        # self.one_pair_strategy[self.num].set_root(visited=True, amount=self.amount, exchange=self.exchange)
        # self.one_pair_strategy.build_tree()
        # print(str(self.one_pair_strategy.root))
        
        # Wyswietlenie drzewa decyzyjnego po zakonczeniu gry
        num_1 = 0

        if self.tree_visible == True:
            print("-"*100)

        for strategy in self.one_pair_strategy:
            if self.tree_visible == True:
                print("Liczba wymienionych kart: " + str(self.amount_list[num_1]) 
                    + "\nCzy wymienic? " + str(self.exchange_list[num_1]))
                print("\n")
                
            strategy.set_root(visited=True, amount=self.amount_list[num_1], exchange=self.exchange_list[num_1])
            strategy.build_tree()
            
            if self.tree_visible == True:
                print(str(strategy.root))
            
            if self.tree_visible == True:
                print("\n")
                print("-"*100)
            num_1 += 1

    def set_cards(self):
        self.cards = [[Card("2", "Ka"),
                      Card("5", "Pi"),
                      Card("9", "Ka"),
                      Card("2", "Tr"),
                      Card("7", "Ki")],
                      [Card("8", "Ka"),
                      Card("8", "Pi"),
                      Card("9", "Tr"),
                      Card("10", "Tr"),
                      Card("6", "Ki")]]

    def remove_all_but_one(self, lst, value):
        count = 0
        result = []
        for item in lst:
            if item == value:
                count += 1
                if count == 1:
                    result.append(item)
            else:
                result.append(item)
        return result
    
    # Losowanie ukladow z puli wygenerowanych kombinacji (Jedna Para) przed poczatkiem gry
    def random_arrangement(self):  
        self.cards = [self.all_comb_perm[self.rand_i],  
                self.all_comb_perm[self.rand_j]]

        idx1 = 0
        idx2 = 0
        
        iter_idx = 0
        if_not_the_same = True
        repeat = 0
        
        # Jesli wylosowany uklad jest taki sam jak uklad drugiego gracza, to nastepuje zmiana
        while(if_not_the_same):
            idx1 = 0
            
            while idx1 < len(self.cards[0]):
                idx2 = 0
                repeat = 0
                while idx2 < len(self.cards[1]):
                    if self.cards[0][idx1] == self.cards[1][idx2]:
                        repeat += 1
                        self.cards[1] = []
                        self.cards[1] = self.all_comb_perm[random.sample(range(0, len(self.all_comb_perm)-1), 1)[0]]
                        
                        iter_idx=0
                        idx1 = 0
                        break
                    
                    if iter_idx == 19 and repeat == 0:
                        if_not_the_same = False
                    iter_idx += 1
                    idx2 += 1
                if repeat == 0:
                    idx1 += 1 
                        
                iter_idx += 1               
                
                
        # print("Wylosowany uklad: ", rand_int)
        # print("Ilosc ukladow: ", len(all_comb_perm))
        # for idx in range(0, len(cards[0])):
        #     cards[0][idx].print()
        # print()
        # for idx in range(0, len(cards[1])):
        #     cards[1][idx].print()
        # print()
        # print()
        
        return self.cards
                
    def set_players_nicknames(self):
        #self.idx_players = int(input("Ilu graczy: "))
        self.idx_players = 2
    
        self.deck = Deck()
        # Jesli wybrano opcje zbierania rozgrywek to lista all_comb_perm nie jest pusta
        if len(self.all_comb_perm) != 0:
            self.cards = self.random_arrangement()

        for idx in range(int(self.idx_players)):
            if idx == 0:
                if self.game_si_human == 2:
                    nick = 'Nick'
                    self.players.append(Player(deck=self.deck, perm=True, nick=nick, index=idx, cards=self.cards[idx],
                                                        if_deck=False, if_show_perm=False, si_boolean=True))
                elif self.game_si_human == 1 or self.game_si_human == 3:   
                    nick = str(input("Pseudonim gracza: "))
                    self.players.append(Player(deck=self.deck, perm=True, nick=nick, index=idx, cards=self.cards[idx],
                                if_deck=False, if_show_perm=False, si_boolean=False))
                else:
                    nick = str(input("Pseudonim gracza: "))
                    print("Dlugosc listy 'all_comb_perm' wynosi: ", len(self.all_comb_perm))
                    self.players.append(Player(deck=self.deck, perm=True, nick=nick, index=idx,
                                if_deck=False, if_show_perm=False, si_boolean=False))
                
            if idx == 1:
                if self.game_si_human == 1 or self.game_si_human == 2:
                    nick = 'Adam'
                    self.players.append(Player(deck=self.deck, perm=True, nick=nick, index=idx, cards=self.cards[idx],
                                                        if_deck=False, if_show_perm=False, si_boolean=True))
                elif self.game_si_human == 3:
                    nick = str(input("Pseudonim gracza: "))
                    self.players.append(Player(deck=self.deck, perm=True, nick=nick, index=idx, cards=self.cards[idx],
                                if_deck=False, if_show_perm=False, si_boolean=False))
                else:
                    nick = str(input("Pseudonim gracza: "))
                    print("Dlugosc listy 'all_comb_perm' wynosi: ", len(self.all_comb_perm))
                    self.players.append(Player(deck=self.deck, perm=True, nick=nick, index=idx,
                                if_deck=False, if_show_perm=False, si_boolean=False))

            #self.deck.print()

    def cards_check_exchange_add_weights(self):
        for self.player in self.players:
            if self.game_visible == True:
                self.player.print(False)
            
            # Ustawienie wag oraz wyswietlenie rodzaju ukladu 
            self.player.arrangements.check_arrangement(game_visible=self.game_visible)
            self.player.arrangements.set_weights()
           
            if self.game_visible == True:
                print()

            #print(self.player.arrangements.get_weight())
            
            # Jesli gra SI to do zmiennej exchange przypisywany jest losowy wynik 
            # zgodnie z drzewem decyzyjnym
            
            if self.player.si_boolean == True:
                self.exchange = np.random.choice(['n', 't'], size=1, 
                                    p=[float(self.one_pair_strategy[self.num].root.internal_nodes[0][0].branches[0]),
                                       float(self.one_pair_strategy[self.num].root.internal_nodes[0][0].branches[1])])    
            else:
                self.exchange = str(input("Wymiana kart [T/N]: ")).lower()            
            
            self.exchange_list.append(self.exchange)

            if self.game_visible == True:
                print(self.exchange)
                print("Wymiana kart: ", self.exchange)  
            
            # Wymiana kart lub nie
            if self.exchange == 't':
                self.cards_exchange()
            if self.exchange == 'n':
                self.amount_list.append(0)
                self.player.arrangements.data_frame_ml.exchange = self.exchange
                [self.player.arrangements.data_frame_ml.set_cards_after(0) for i in range(0, 5)]
                [self.player.arrangements.data_frame_ml.set_cards_exchanged(0) for i in range(0, 3)]


            
            self.num += 1
            
            # Przypisanie do ramki danych liczby kart do wymiany dla danego gracza
            [self.player.arrangements.data_frame_ml.set_exchange_amount(self.amount_list[al_idx]) for al_idx in range(0, len(self.amount_list))]

            # Dodanie do listy wagi ukladu danego gracza
            self.weights.append(self.player.arrangements.get_weight())
            
            # Przypisanie do ramki danych wymienionych kart dla danego gracza
            [self.player.arrangements.data_frame_ml.set_cards_exchanged(card.weight) for card in self.player.cards_exchanged]
            if self.game_visible == True:
                print()
                print("------------------------------------------------------------")
                print()

    # Rozdawanie kart do graczy
    def deal_cards(self):
        for idx in range(self.amount):
            self.player.take_cards(self.deck)

    def cards_exchange(self):
       
        # Preprocessing danych do przewidywania prawdopodobienstwa wygranej gracza
        if self.player.si_boolean == True:
            
            if self.prediction_mode == True:
                # Otwarcie pliku z zaktualizowanymi modelami
                with open('models_prediction/path_to_model_WIN.txt', 'r') as file:
                    filename_updated = file.readline()
                    
                    if not filename_updated:
                        filename_updated = ''

                # Wczytanie modelu w zaleznosci od tego czy zaktualizowany model istnieje
                if os.path.exists(filename_updated):
                    saved_model = tf.keras.models.load_model(filename_updated)
                else:
                    directory = "models_prediction"
                    prefix = "model_base_WIN"
                    extension = "keras"
                    pattern = rf"^{prefix}.*\.{extension}$"
                    matching_file = [filename for filename in os.listdir(directory) if re.match(pattern, filename)]

                    print("Pasujace wzorce (regexp):", matching_file)

                    saved_model = tf.keras.models.load_model(directory + '/' + matching_file[0])

                    saved_model.load_weights('models_prediction/weights_model_base_WIN_Adam_0001_test_acc=0.667_test_loss=0.155_2024-08-14_08-52-13.weights.h5')
                                    
                cards_player_sorted = sorted(self.player.cards) 

                for amount in range(2, 3 + 1):   
                    self.X_game = pd.DataFrame({'Exchange' : self.exchange, 
                                    'Exchange Amount_0' : [True] if amount == 0 else [False],
                                    'Exchange Amount_2' : [True] if amount == 2 else [False],
                                    'Exchange Amount_3' : [True] if amount == 3 else [False],
                                    })
                
                    self.X_game.loc[self.X_game['Exchange'] == ['t'], 'Exchange'] = True
                    self.X_game.loc[self.X_game['Exchange'] == ['n'], 'Exchange'] = False  
                
                    self.X_game['Exchange Amount' + '_' + str(amount)] = 1  

                    for idx1 in range(0, 5):
                        for idx2 in range(1, 14):
                            if idx2 != cards_player_sorted[idx1].weight:
                                self.X_game['Cards Before '+ str(idx1+1) + '_' + str(idx2)] = 0
                            else:
                                self.X_game['Cards Before '+ str(idx1+1) + '_' + str(idx2)] = 1

                    if 'Exchange Amount_0' not in self.X_game.columns:
                        self.X_game['Exchange Amount_0'] = 0
                    if 'Exchange Amount_2' not in self.X_game.columns:
                        self.X_game['Exchange Amount_2'] = 0
                    if 'Exchange Amount_3' not in self.X_game.columns:
                        self.X_game['Exchange Amount_3'] = 0 
                    
                    self.X_game = self.X_game.astype(np.int64)

                    y_preds = saved_model.predict(self.X_game).flatten()

                    if self.game_visible == True:
                        logging.getLogger("tensorflow").setLevel(logging.ERROR)

                    # Prawdopodobienstwo wygranej z dwiena lub trzema kartami
                    if self.game_visible == True:
                        print("Szansa na wygrana przy wymianie " + str(amount) + " kart: ", y_preds * 100)
            
            # Wybieranie ilosci kart do wymiany zgodnie z prawdopodobienstwem
            self.amount = np.random.choice([2, 3], size=1, 
                                    p=[float(self.one_pair_strategy[self.num].root.internal_nodes[1][0].branches[0]),
                                       float(self.one_pair_strategy[self.num].root.internal_nodes[1][0].branches[1])])
            
            self.amount = int(self.amount)
        
        # Gracz: Czlowiek
        else:
            self.amount = int(input("Ile kart do wymiany [0-5][-1 COFNIJ]: "))
            
            #saved_model = tf.keras.models.load_model('models_prediction/model_base_WIN_Adam_00001_test_acc=0.666_test_loss=0.155.keras')
            # if self.all_comb_perm == 0:
            #     cards_player_sorted = sorted(self.player.cards)

            #     for amount in range(2, 3 + 1): 
            #         X_game = pd.DataFrame({'Exchange' : [self.exchange], 
            #                             'Card Before 1' : [cards_player_sorted[0].weight],
            #                             'Card Before 2' : [cards_player_sorted[1].weight],
            #                             'Card Before 3' : [cards_player_sorted[2].weight],
            #                             'Card Before 4' : [cards_player_sorted[3].weight],
            #                             'Card Before 5' : [cards_player_sorted[4].weight],
            #                             'Exchange Amount_0' : [True] if amount == 0 else [False],
            #                             'Exchange Amount_2' : [True] if amount == 2 else [False],
            #                             'Exchange Amount_3' : [True] if amount == 3 else [False],
            #                             })
                    
            #         X_game.loc[X_game['Exchange'] == ['t'], 'Exchange'] = True
            #         X_game.loc[X_game['Exchange'] == ['n'], 'Exchange'] = False        

            #         X_game = X_game.astype(np.int64)

            #         if self.game_visible == False:
            #             logging.getLogger("tensorflow").setLevel(logging.ERROR)
                    
            #         y_preds = saved_model.predict(X_game, verbose=0)
                    
            #         if self.game_visible == True:
            #             print("Szansa na wygrana przy wymianie " + str(amount) + " kart: ", y_preds * 100)
                
    
        self.amount_list.append(self.amount)
        
        if self.game_visible == True:
            print("Ile kart do wymiany: ", self.amount)
            print()

        if self.amount == -1:
            return

        # Zwracanie kart do krupiera w zaleznosci od tego czy to gracz SI czy Czlowiek
        self.amount = self.player.return_to_croupier(self.amount, 
                                                     self.player.arrangements.get_part_weight(), game_visible=False,
                                                     si_boolean=self.player.si_boolean)
        if self.game_visible == True:
            print(self.amount)
            
        # Rozdawanie kart przez krupiera
        self.deal_cards()

        # Przypisanie nowych kart dla klasy Arrangements
        self.player.arrangements.set_cards(self.player.cards)
        
        if self.game_visible == True:
            print()
            print("------------------------------------------------------------")
            print()

            self.player.print(False)
            
        self.player.arrangements.check_arrangement(game_visible=self.game_visible)
        self.player.arrangements.set_weights()
        
        # Inicjalizacja ramki danych 
        self.player.arrangements.data_frame_ml.exchange = self.exchange
        self.player.arrangements.init_data_frame_ml_after_ex()

    def compare_players_weights(self):
        # Okreslenie maksymalnej wagi z danych wag kart
        max_weight = list(max(enumerate(self.weights), key = itemgetter(1)))
        
        if self.game_visible == True:
            print("Wieksza waga: ", max_weight)

            print()
            print("------------------------------------------------------------")
            print("------------------------------------------------------------")
            print()

        for self.player in self.players:

            if self.player.index == max_weight[0]:
                if self.game_visible == True:
                    print("WYGRANA")
                
                self.player.arrangements.set_cards(self.player.cards)
                self.player.win_or_not = True

                if self.game_visible == True:
                    self.player.print(False)
                
                self.player.arrangements.check_arrangement(game_visible=self.game_visible)

            else:
                self.player.win_or_not = False
            
            self.player.arrangements.data_frame_ml.win_or_not = self.player.win_or_not

        for self.player in self.players:
            if self.tree_visible == True or self.game_visible == True:
                #self.player.arrangements.get_data_frame_ml().print()
                pass
            self.player.arrangements.get_data_frame_ml().save_to_csv("ml_data/poker_game_one_pair_combs_all_to_update_duplicates.csv")







