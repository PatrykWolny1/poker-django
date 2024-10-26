from decision_tree_strategies.ComputeObject import ComputeObject

class TwoThreeCardsProbability(ComputeObject):
    
    def __init__(self, name: str = '', threshold: float = 0, result_var: float = 0, data = None, p1: float = 0.2):
        super().__init__(name, result_var, data)
        self.threshold:int = threshold
        self.p1:float = p1
    def computing(self):
        count_1 = 0

        for idx in range(0, len(self.data)):
            if self.data[idx] < self.threshold:
                count_1 += 1
            else:
                self.data[idx] = None
                


        if count_1 == 2 or count_1 == 1:
            self.p1 = 0
        if count_1 == 3:
            self.p1 = -self.p1
        
        
        self.result_var = [1 - (count_1/len(self.data)) - self.p1, count_1/len(self.data) + self.p1] 
    
    def result(self):
        return self.result_var
    
    def get_proc_data(self):
        self.data = list(filter(None, self.data))
        return self.data
    
    def get_all_data(self):
        return self.data
