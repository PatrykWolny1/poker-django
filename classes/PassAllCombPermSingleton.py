
class PassAllCombPermSingleton:
    def __init__(self):
        self.all_comb_perm = None
        
    def set_all_comb_perm(self, all_comb_perm):
        self.all_comb_perm = all_comb_perm
    
    def get_all_comb_perm(self):
        return self.all_comb_perm

pass_all_comb_perm = PassAllCombPermSingleton()        
        


