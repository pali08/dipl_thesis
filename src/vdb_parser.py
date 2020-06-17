from src.global_constants_and_functions import METALS
from src.json_parser import JsonParser


class VdbParser(JsonParser):
    def __init__(self, filename):
        super().__init__(filename)

    def detect_metal(self, model_num):
        """
        detects metal in model for given vdb file.
        :param model_num: number of model
        :return: true (bool of nonempty list is true, bool of empty is False)
        """
        return bool(
            {i.lower() for i in self.json_dict['Models'][model_num]['ModelAtomTypes'].values()}.intersection(METALS))

    def get_counts(self):
        ligand_count_filtered = float(self.json_dict['MotiveCount'])
        missing_atom_count = len([self.json_dict['Models'][i]['Entries'][j]['MissingAtoms'][k] for i in
                                  range(0, len(self.json_dict['Models'])) for j in
                                  range(0, len(self.json_dict['Models'][i]['Entries'])) for k in
                                  self.json_dict['Models'][i]['Entries'][j]['MissingAtoms']])
        total_atom_count = len([j for i in self.json_dict['Models'] for j in i['ModelAtomTypes']])
        total_atom_count_metal_ligands = sum(map(len, [self.json_dict['Models'][i]['ModelAtomTypes'] for i in
                                                       range(0, len(self.json_dict['Models'])) if
                                                       self.detect_metal(i)]))
        wrong_chiral_count = [l for l in [self.json_dict['Models'][i]['Entries'][j]['ChiralityMismatches'][k] for i in
                                          range(0, len(self.json_dict['Models'])) for j in
                                          range(0, len(self.json_dict['Models'][i]['Entries'])) for k in
                                          self.json_dict['Models'][i]['Entries'][j]['ChiralityMismatches'].keys()] if
                              len(l) > 1 and l.split()[1].upper() == "C"]
