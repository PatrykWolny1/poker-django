from classes.Card import Card
import random

class Deck(object):
    def __init__(self):
        self.markings:tuple = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')
        self.colors:tuple = ('Ki', 'Tr', 'Ka', 'Pi')
        self.weight:tuple = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
        self.cards:list = []
        self.num:int = 0
        self.idx_1:int = 0
        
        for color in self.colors:
            for marking in self.markings:
                self.cards.append(Card(marking, color))
        self.counter:int = 0
    def print(self):
        for i in range(len(self.cards)):
            print(i + 1, self.cards[i].print_str())
        print()

    def shuffling(self):
        random.shuffle(self.cards)

    def deal(self):   

        card = self.cards[self.counter]
        self.cards.pop(self.counter)
        self.counter = self.counter + 1

        return card
    
    def pop_from_deck(self, cards_list: list = []):
        idx = 0
        for num in range(0, len(cards_list)):
            idx = 0
            while (idx < len(self.cards)):
                if cards_list[num].name == self.cards[idx].name and cards_list[num].color == self.cards[idx].color:
                    self.cards.pop(idx)        
                    #print(idx+1)
                    idx -= 1
                idx += 1
        #self.print()
                
