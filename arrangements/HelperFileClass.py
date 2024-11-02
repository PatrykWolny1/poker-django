from pathlib import Path

class HelperFileClass:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_path_dst = Path('permutations_data/data_permutations_combinations.txt')