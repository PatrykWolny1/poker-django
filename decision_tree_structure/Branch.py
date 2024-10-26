class Branch(object):
    
    def __init__(self, name: str = '', threshold: float = 0):
        self.name = name
        self.threshold = threshold  
    
    def __str__(self):
        return self.name + "(" + str("{:.4f}".format(self.threshold)) + ")" 
    
    def __float__(self):
        return self.threshold   
          