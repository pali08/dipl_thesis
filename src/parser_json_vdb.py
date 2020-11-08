from src.global_constants_and_functions import METALS, division_zero_div_handling, NAN_VALUE, is_float
from src.parser_json import JsonParser


def get_binary(value, topval):
    if type(value) == float or type(value) == int:
        if topval == 0:
            return int(bool(value))
        if topval == 1 and value == 1:
            return topval
        return 0
    else:
        return NAN_VALUE


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
                            'ligandBondRotationFreedom': NAN_VALUE,
                            'ChiralProblemLigandRatio': NAN_VALUE,
                            'GoodLigandRatio': NAN_VALUE,
                            'TopologyProblemLigandRatio': NAN_VALUE,
                            'LigandTopologyProblemsPrecise': NAN_VALUE,
                            'LigandTopologyCarbonChiraProblemsPrecise': NAN_VALUE,
                            'ChiraProblemsPrecise': NAN_VALUE,
                            'GoodLigandRatioBinary': NAN_VALUE,
                            'LigandTopologyProblemsPreciseBinary': NAN_VALUE,
                            'LigandTopologyCarbonChiraProblemsPreciseBinary': NAN_VALUE,
                            'ChiraProblemsPreciseBinary': NAN_VALUE
                            }
        if super().file_exists():
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
            ligand_count_filtered = int((self.json_dict['MotiveCount']))  # = motiveCount
        except KeyError:
            ligand_count_filtered = NAN_VALUE
            print(self.key_error_output('ligand count filtered'))
        try:
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
        except KeyError:
            total_atom_count = NAN_VALUE
            total_atom_count_metal_ligands = NAN_VALUE
            print(self.key_error_output('hetatm count filtered (metal)'))
        try:
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
        ligand_count_filtered_nometal = int(ligand_count_filtered - motive_count_metal_ligands)

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

    def get_undivided_data(self):
        chiral_problem_ligand_ratio = division_zero_div_handling(
            sum([self.json_dict['Models'][i]['Summary']['HasAll_BadChirality_Carbon'] for i in
                 range(0, len(self.json_dict['Models']))]), self.result_dict['ligandCountFiltered'])
        missing_atoms = sum(
            [self.json_dict['Models'][i]['Summary']['Missing_Atoms'] for i in
             range(0, len(self.json_dict['Models']))])
        missing_rings = sum(
            [self.json_dict['Models'][i]['Summary']['Missing_Rings'] for i in
             range(0, len(self.json_dict['Models']))])
        missing_atoms_rings = missing_atoms + missing_rings
        good_ligand_count = (self.result_dict['ligandCountFiltered'] - sum(
            [self.json_dict['Models'][i]['Summary']['HasAll_BadChirality_Carbon'] for i in
             range(0, len(self.json_dict['Models']))])) - missing_atoms_rings
        good_ligand_ratio = division_zero_div_handling(good_ligand_count, self.result_dict['ligandCountFiltered'])
        topology_problem_ligand_ratio = division_zero_div_handling(missing_atoms_rings,
                                                                   self.result_dict['ligandCountFiltered'])
        missing_atom_count = len([self.json_dict['Models'][i]['Entries'][j]['MissingAtoms'][k] for i in
                                  range(0, len(self.json_dict['Models'])) for j in
                                  range(0, len(self.json_dict['Models'][i]['Entries'])) for k in
                                  range(0, len(self.json_dict['Models'][i]['Entries'][j]['MissingAtoms']))])
        missing_atom_ratio = division_zero_div_handling(missing_atom_count, self.result_dict['hetatmCountFiltered'])
        wrong_c_chira_count = len([
            list(self.json_dict['Models'][i]['Entries'][j]['ChiralityMismatches'].values())[k].split()[1] for i in
            range(0, len(self.json_dict['Models'])) for j in
            range(0, len(self.json_dict['Models'][i]['Entries'])) for k in
            range(0, len(self.json_dict['Models'][i]['Entries'][j]['ChiralityMismatches'].values())) if
            list(self.json_dict['Models'][i]['Entries'][j]['ChiralityMismatches'].values())[k].split()[1] == 'C'])
        total_c_chira_count = sum(
            [len(self.json_dict['Models'][i]['ChiralAtomsInfo']['Carbon']) * len(self.json_dict['Models'][i]['Entries'])
             for i in range(0, len(self.json_dict['Models']))])
        carbon_chira_problem_ratio = NAN_VALUE
        both_problem_ratio = NAN_VALUE
        if total_c_chira_count != 0:
            carbon_chira_problem_ratio = division_zero_div_handling(wrong_c_chira_count,
                                                                    total_c_chira_count)  # ChiraProblemsPrecise
            both_problem_ratio = sum([float(i) for i in [carbon_chira_problem_ratio, missing_atom_ratio] if
                                      is_float(i) if is_float(i)])  # LigandTopologyCarbonChiraProblemsPrecise
        elif self.result_dict['hetatmCountFiltered'] != 0:
            carbon_chira_problem_ratio = 0
            both_problem_ratio = 0
        good_ligand_ratio_binary = get_binary(good_ligand_ratio, 1)
        missing_atom_ratio_binary = get_binary(missing_atom_ratio, 0)
        both_problem_ratio_binary = get_binary(both_problem_ratio, 0)
        carbon_chira_problem_ratio_binary = get_binary(carbon_chira_problem_ratio, 0)
        self.result_dict.update(
            {'ChiralProblemLigandRatio': chiral_problem_ligand_ratio,
             'GoodLigandRatio': good_ligand_ratio,
             'TopologyProblemLigandRatio': topology_problem_ligand_ratio,
             'LigandTopologyProblemsPrecise': missing_atom_ratio,
             'LigandTopologyCarbonChiraProblemsPrecise': both_problem_ratio,
             'ChiraProblemsPrecise': carbon_chira_problem_ratio,
             'GoodLigandRatioBinary': good_ligand_ratio_binary,
             'LigandTopologyProblemsPreciseBinary': missing_atom_ratio_binary,
             'LigandTopologyCarbonChiraProblemsPreciseBinary': both_problem_ratio_binary,
             'ChiraProblemsPreciseBinary': carbon_chira_problem_ratio_binary})

    def create_result_dict(self):
        self.get_counts()
        self.get_undivided_data()
