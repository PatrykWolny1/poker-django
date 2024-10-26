from abc import abstractmethod

class ComputeObject(object):
    
    def __init__(self, name: str = '', result_var: float = 0, data = None):
        self.name:str = name
        self.data:None = data
        self.result_var:float = result_var
    
    @abstractmethod
    def computing(self):
        pass
    
    @abstractmethod
    def result(self):
        return self.result_var
    
    def __add__(self, other):
        return self.result_var + other.result_var
