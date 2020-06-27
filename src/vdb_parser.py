from src.global_constants_and_functions import METALS, division_zero_div_handling
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
        total_c_chiral_count = sum(map(len, [self.json_dict['Models'][i]['ChiralAtomsInfo']['Carbon'] for i in
                                             range(len(self.json_dict['Models']))]))
        motive_count_metal_ligands = sum(map(len, [self.json_dict['Models'][i]['Entries'] for i in
                                                   range(len(self.json_dict['Models']))]))
        total_bond_count = sum(map(len, [self.json_dict['Models'][i]['ModelBonds'] for i in
                                         range(0, self.json_dict['Models'])]))
        sigma_bond_count = sum(map(len, [[value for key, value in self.json_dict['Models'][i]['ModelBonds'].items()
                                          if value == 1] for i in
                                         range(0, self.json_dict['Models'])]))
        ligand_bond_rotation_freedom = division_zero_div_handling(sigma_bond_count / total_bond_count)

        return {'ligand_count_filtered': ligand_count_filtered, 'missing_atom_count': missing_atom_count,
                'total_atom_count': total_atom_count, 'total_atom_count_metal_ligands': total_atom_count_metal_ligands,
                'wrong_chiral_count': wrong_chiral_count, 'total_c_chiral_count': total_c_chiral_count,
                'motive_count_metal_ligands': motive_count_metal_ligands, 'total_bond_count': total_bond_count,
                'sigma_bond_count': sigma_bond_count, 'ligand_bond_rotation_freedom': ligand_bond_rotation_freedom}
