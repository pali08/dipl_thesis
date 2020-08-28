from src.global_constants_and_functions import METALS, division_zero_div_handling, NAN_VALUE
from src.json_parser import JsonParser


class VdbParser(JsonParser):
    def __init__(self, filename):
        super().__init__(filename)
        self.result_dict = {'hetatmCountFiltered': NAN_VALUE, 'ligandCarbonChiraAtomCountFiltered': NAN_VALUE,
                            'ligandCountFiltered': NAN_VALUE, 'ligandRatioFiltered': NAN_VALUE,
                            'ligandRatioFilteredMetal': NAN_VALUE,
                            'ligandRatioFilteredNometal': NAN_VALUE,
                            'hetatmCountFilteredMetal': NAN_VALUE,
                            'hetatmCountFilteredNometal': NAN_VALUE,
                            'ligandCountFilteredNometal': NAN_VALUE,
                            'ligandCountFilteredMetal': NAN_VALUE,
                            'ligandBondRotationFreedom': NAN_VALUE}
        self.create_result_dict()

    def detect_metal(self, model_num):
        """
        detects metal in model for given vdb file.
        :param model_num: number of model
        :return: true (bool of nonempty list is true, bool of empty is False)
        """
        return bool(
            {i.lower() for i in self.json_dict['Models'][model_num]['ModelAtomTypes'].values()}.intersection(METALS))

    def get_counts(self):
        try:
            ligand_count_filtered = float(self.json_dict['MotiveCount'])  # = motiveCount
        except KeyError:
            ligand_count_filtered = NAN_VALUE
            print(self.key_error_output('ligand count filtered'))
        try:
            # total_atom_count = len([j for i in self.json_dict['Models'] for j in i['ModelAtomTypes']])
            total_atom_count = sum(
                [len(self.json_dict['Models'][i]['ModelAtomTypes']) * len(self.json_dict['Models'][i]['Entries']) for i
                 in range(0, len(self.json_dict['Models']))])
            total_atom_count_metal_ligands_modelatomtypes = map(len,
                                                                [self.json_dict['Models'][i]['ModelAtomTypes'] for i in
                                                                 range(0, len(self.json_dict['Models'])) if
                                                                 self.detect_metal(i)])
            total_atom_count_metal_ligands_entries = map(len, [self.json_dict['Models'][i]['Entries'] for i in
                                                               range(0, len(self.json_dict['Models'])) if
                                                               self.detect_metal(i)])
            total_atom_count_metal_ligands = sum([i * j for i, j in
                                                  zip(total_atom_count_metal_ligands_modelatomtypes,
                                                      total_atom_count_metal_ligands_entries)])
            # print(total_atom_count_metal_ligands)
        except KeyError:
            total_atom_count = NAN_VALUE
            total_atom_count_metal_ligands = NAN_VALUE
            print(self.key_error_output('hetatm count filtered (metal)'))
        try:
            # total_c_chiral_count = sum(map(len, [self.json_dict['Models'][i]['ChiralAtomsInfo']['Carbon'] for i in
            #                                      range(len(self.json_dict['Models']))]))
            total_c_chiral_count = sum([len(self.json_dict['Models'][i]['ChiralAtomsInfo']['Carbon']) * len(
                self.json_dict['Models'][i]['Entries']) for i in range(0, len(self.json_dict['Models']))])
        except KeyError:
            total_c_chiral_count = NAN_VALUE
            print(self.key_error_output('ligand Carbon Chiral Atom Count Filtered'))
        try:
            motive_count_metal_ligands = sum(map(len, [self.json_dict['Models'][i]['Entries'] for i in
                                                       range(len(self.json_dict['Models'])) if self.detect_metal(i)]))
        except KeyError:
            motive_count_metal_ligands = NAN_VALUE
            print(self.key_error_output('ligand count filtered metal'))
        try:
            total_bond_count = sum(map(len, [self.json_dict['Models'][i]['ModelBonds'] for i in
                                             range(0, len(self.json_dict['Models']))]))
            sigma_bond_count = sum(map(len, [[value for key, value in self.json_dict['Models'][i]['ModelBonds'].items()
                                              if value == 1] for i in
                                             range(0, len(self.json_dict['Models']))]))
        except KeyError:
            total_bond_count = NAN_VALUE
            sigma_bond_count = NAN_VALUE
            print(self.key_error_output('total/sigma bound count'))
        ligand_bond_rotation_freedom = division_zero_div_handling(sigma_bond_count, total_bond_count)
        ligand_ratio_filtered = division_zero_div_handling(total_atom_count, ligand_count_filtered)
        total_atom_count_nometal_ligands = total_atom_count - total_atom_count_metal_ligands
        motive_count_nometal_ligands = ligand_count_filtered - motive_count_metal_ligands
        ligand_ratio_filtered_nometal = division_zero_div_handling(total_atom_count_nometal_ligands,
                                                                   motive_count_nometal_ligands)
        ligand_ratio_filtered_metal = division_zero_div_handling(total_atom_count_metal_ligands,
                                                                 motive_count_metal_ligands)
        hetatm_count_filtered_nometal = total_atom_count - total_atom_count_metal_ligands
        ligand_count_filtered_nometal = ligand_count_filtered - motive_count_metal_ligands

        self.result_dict.update(
            {'hetatmCountFiltered': total_atom_count, 'ligandCarbonChiraAtomCountFiltered': total_c_chiral_count,
             'ligandCountFiltered': ligand_count_filtered, 'ligandRatioFiltered': ligand_ratio_filtered,
             'ligandRatioFilteredMetal': ligand_ratio_filtered_metal,
             'ligandRatioFilteredNometal': ligand_ratio_filtered_nometal,
             'hetatmCountFilteredMetal': total_atom_count_metal_ligands,
             'hetatmCountFilteredNometal': hetatm_count_filtered_nometal,
             'ligandCountFilteredNometal': ligand_count_filtered_nometal,
             'ligandCountFilteredMetal': motive_count_metal_ligands,
             'ligandBondRotationFreedom': ligand_bond_rotation_freedom})

    def create_result_dict(self):
        if super().file_exists():
            self.get_counts()
