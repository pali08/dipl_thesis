from src.json_parser import JsonParser


class VdbParser(JsonParser):
    def __init__(self, filename):
        super().__init__(filename)

    def get_counts(self):
        ligand_count_filtered = float(self.json_dict['MotiveCount'])



