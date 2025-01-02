from pathlib import Path

class HelperFileClass:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_path_dst = None

    def set_session_id(self, session_id):
        self.file_path_dst = Path(f'permutations_data/data_perms_combs_ID_{session_id}.txt')