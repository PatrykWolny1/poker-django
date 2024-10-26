class Card(object):

    def __init__(self, name:str = None, color:str = None, weight:None = None, empty:bool = False):
        self.markings:dict = (['2', 1], ['3', 2], ['4', 3], ['5', 4], ['6', 5], ['7', 6], ['8', 7],
                    ['9', 8], ['10', 9], ['J', 10], ['Q', 11], ['K', 12], ['A', 13])
        if empty == False:
            self.weight:tuple = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)      
      
        #Dodawanie wag i nazw

        for idx1 in range(0, len(self.markings)):
            for idx2 in range(0, len(self.markings[idx1])):
                if name == self.markings[idx1][0]:
                    self.weight = self.markings[idx1][1]
                    #self.name_weight = self.markings[idx1][1] + 1
        self.name:str = name
        self.color:str = color
        
        if empty == True:
            self.weight:int = weight

    def __lt__(self, other):
        return self.weight < other.weight

    # @property
    # def weight(self):
    #     return self.weight

    def print(self):
        print(self.name, end = "")
        print(self.color, end = " ")

    def print_str(self):
        str = self.name + self.color + ""
        return str