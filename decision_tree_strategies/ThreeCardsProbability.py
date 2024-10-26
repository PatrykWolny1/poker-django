from decision_tree_strategies.ComputeObject import ComputeObject

class ThreeCardsProbability(ComputeObject):
    
    def __init__(self, name: str = '', result_var: float = 0, data = None, threshold: int = 0, p1: float = 0.01):
        super().__init__(name, result_var, data)
        self.threshold:int = threshold
        self.p1:float = p1
        
    def computing(self):
        if max(self.data) > self.threshold:
            self.result_var = self.p1
            
    def result(self):
        return self.result_var