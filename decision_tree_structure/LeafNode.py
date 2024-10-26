class LeafNode(object):
    
    def __init__(self, name: str, result = None):
        self.name = name
        self.result = result
        
    def __str__(self):
        return self.name
    
    def __float__(self):
        return self.result  