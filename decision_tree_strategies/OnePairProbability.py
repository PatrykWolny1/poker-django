from decision_tree_strategies.ComputeObject import ComputeObject
from scipy.special import binom

class OnePairProbability(ComputeObject):
    
    def __init__(self, name: str = '', result_var: float = 0, data = None, nk: list = None):
        super().__init__(name, result_var, data)
        self.nk:list = nk
        
    def computing(self):
        binom_list = []

        for idx in range(0, len(self.nk)):
            binom_list.append(binom(self.nk[idx][0], self.nk[idx][1]))
        
        Px = (binom_list[0] * binom_list[1]) / binom_list[2]
                
        self.result_var = Px  
        
    def result(self):
        return self.result_var

