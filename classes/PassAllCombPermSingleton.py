import pickle

class PassAllCombPermSingleton:
    def __init__(self):
        self.all_comb_perm = None
        
    def set_all_comb_perm(self, all_comb_perm):
        self.all_comb_perm = all_comb_perm
    
    def get_all_comb_perm(self):
        return self.all_comb_perm
    
    def set_pickle_combs_one_pair_game(self, session_id):
        with open(f"combinations_one_pair_game_{session_id}.pkl", "wb") as file:
            pickle.dump(self, file)

    def get_pickle_combs_one_pair_game(self, session_id):
        with open(f"combinations_one_pair_game_{session_id}.pkl", "rb") as file:
            loaded_object = pickle.load(file)
        return loaded_object.all_comb_perm
    
pass_all_comb_perm = PassAllCombPermSingleton()        
        


