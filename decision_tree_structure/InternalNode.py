class InternalNode(object):

    def __init__(self, name: str, branches = None, leaf_nodes = None):
        self.name = name
        self.branches = branches
        self.leaf_nodes = leaf_nodes
        
    def __str__(self) -> str:
        return self.name