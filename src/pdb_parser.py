import numpy as np
from Bio.File import as_handle
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from src.global_constants_and_functions import METALS, WATER_MOLECULE, division_zero_div_handling, to_float, to_int, \
    NAN_VALUE, addition_nan_handling, subtraction_nan_handling, is_float, multiplying_question_mark_handling
from src.parser import Parser


def get_mmcif_dictionary(filename):
    def get_mmcif_dictionary_local_function(fnm):
        return MMCIF2Dict(fnm)

    try:
        return get_mmcif_dictionary_local_function(filename)
    except UnicodeDecodeError:
        with as_handle(filename, 'r', encoding='utf-16') as f:
            return get_mmcif_dictionary_local_function(f)


class PdbParser(Parser):

    def __init__(self, filename):
        super().__init__(filename)
        self.mmcif_dict = get_mmcif_dictionary(filename)
        self.result_dict = {'PDB ID': NAN_VALUE, 'releaseDate': NAN_VALUE, 'StructureWeight': 0,
                            'PolymerWeight': NAN_VALUE,
                            'NonpolymerWeight': NAN_VALUE,
                            'NonpolymerWeightNowater': NAN_VALUE, 'WaterWeight': NAN_VALUE, 'atomCount': NAN_VALUE,
                            'hetatmCount': NAN_VALUE, 'allAtomCount': NAN_VALUE,
                            'allAtomCountLn': NAN_VALUE, 'aaCount': NAN_VALUE, 'ligandCount': NAN_VALUE,
                            'aaLigandCount': NAN_VALUE, 'aaLigandCountNowater': NAN_VALUE,
                            'ligandRatio': NAN_VALUE, 'hetatmCountNowater': NAN_VALUE,
                            'ligandCountNowater': NAN_VALUE, 'ligandRatioNowater': NAN_VALUE,
                            'hetatmCountMetal': NAN_VALUE, 'ligandCountMetal': NAN_VALUE,
                            'ligandRatioMetal': NAN_VALUE, 'hetatmCountNometal': NAN_VALUE,
                            'ligandCountNometal': NAN_VALUE, 'ligandRatioNometal': NAN_VALUE,
                            'hetatmCountNowaterNometal': NAN_VALUE,
                            'ligandCountNowaterNometal': NAN_VALUE,
                            'ligandRatioNowaterNometal': NAN_VALUE, 'resolution': NAN_VALUE}
        self.create_result_dict()

    def get_pdb_id(self):
        try:
            self.result_dict.update({'PDB ID': self.mmcif_dict['_entry.id'][0].lower()})
        except KeyError:
            pass

    def get_pdb_release_date(self):
        try:
            self.result_dict.update({'releaseDate': to_int(self.mmcif_dict['_citation.year'][0])})
        except KeyError:
            pass

    def get_structure_weights(self):
        """
        Get different structure weights based on type of molecules
        :return: list of weights
        """
        print(self.filename)
        try:
            entities_list = list(zip(self.mmcif_dict['_entity.type'],
                                     [multiplying_question_mark_handling(i[0], i[1]) for i in
                                      list(zip(self.mmcif_dict['_entity.formula_weight'],
                                               self.mmcif_dict[
                                                   '_entity.pdbx_number_of_molecules'
                                               ]))]))
            # debug output:
            polymer_weight = float(sum([i[1] for i in entities_list if i[0] == "polymer"])) / 1000  # in kDaltons
            non_polymer_weight = float(sum([i[1] for i in entities_list if i[0] == "non-polymer"]))  # in Daltons
            water_weight = float(sum([i[1] for i in entities_list if i[0] == "water"]))  # in Daltons
            non_polymer_weight_with_water = non_polymer_weight + water_weight
            structure_weight = polymer_weight + (
                    non_polymer_weight + water_weight) / 1000  # in kDaltons
            self.result_dict.update({'StructureWeight': structure_weight, 'PolymerWeight': polymer_weight,
                                     'NonpolymerWeight': non_polymer_weight_with_water,
                                     'NonpolymerWeightNowater': non_polymer_weight, 'WaterWeight': water_weight})
        except KeyError:
            print(self.key_error_output('weights'))
            pass

    def get_mmcif_resolution(self):
        """
        MMCIF is loaded as dictionary
        :param self.mmcif_dict
        :return: Highest resolution value if exists, nan otherwise.
        Highest resolution can be different item in different file. 2 of possibilities are covered for now
        """
        if '_refine.ls_d_res_high' in self.mmcif_dict:
            self.result_dict.update({'resolution': to_float(self.mmcif_dict['_refine.ls_d_res_high'][0])})
        else:
            self.result_dict.update({'resolution': NAN_VALUE})

    def get_structure_counts(self):
        """
        counts of atoms and ligands
        :return:
        """
        try:
            atom_count = len([i for i in self.mmcif_dict['_atom_site.group_PDB'] if i.upper() == 'ATOM'])
            hetatm_count = len([i for i in self.mmcif_dict['_atom_site.group_PDB'] if i.upper() == 'HETATM'])
        except KeyError:
            atom_count = NAN_VALUE
            hetatm_count = NAN_VALUE
            print(self.key_error_output('Atom and hetatm counts'))
        all_atom_count = addition_nan_handling(atom_count, hetatm_count)
        all_atom_count_ln = round(np.log(all_atom_count),
                                  5) if all_atom_count != 0 and all_atom_count != NAN_VALUE else NAN_VALUE
        try:
            aa_count = len(self.mmcif_dict['_entity_poly_seq.entity_id'])
        except KeyError:
            aa_count = NAN_VALUE
            print(self.key_error_output('aa count'))
        try:
            ligand_count = len(set(
                [(self.mmcif_dict['_atom_site.auth_seq_id'][i], self.mmcif_dict['_atom_site.auth_asym_id'][i]) for i in
                 range(0, len(self.mmcif_dict['_atom_site.auth_seq_id'])) if
                 self.mmcif_dict['_atom_site.group_PDB'][i].upper().strip() == 'HETATM']))
        except KeyError:
            ligand_count = NAN_VALUE
            print(self.key_error_output('ligand count'))
        aa_ligand_count = addition_nan_handling(aa_count, ligand_count)
        try:
            nonwater_ligand_count = len(set(
                [(self.mmcif_dict['_atom_site.auth_seq_id'][i], self.mmcif_dict['_atom_site.auth_asym_id'][i]) for i in
                 range(0, len(self.mmcif_dict['_atom_site.auth_seq_id'])) if
                 self.mmcif_dict['_atom_site.group_PDB'][i].upper() == 'HETATM' and
                 self.mmcif_dict['_atom_site.label_comp_id'][i].upper() != WATER_MOLECULE]))
        except KeyError:
            nonwater_ligand_count = NAN_VALUE
            print(self.key_error_output('nonwater ligand count'))
        aa_ligand_count_nowater = addition_nan_handling(aa_count + nonwater_ligand_count)
        ligand_ratio = division_zero_div_handling(hetatm_count, ligand_count)
        try:
            hetatm_count_nowater = hetatm_count - len(
                [i for i in self.mmcif_dict['_atom_site.label_comp_id'] if i.upper() == WATER_MOLECULE])
        except KeyError:
            hetatm_count_nowater = NAN_VALUE
            print(self.key_error_output('hetatm count nowater'))
        ligand_count_nowater = nonwater_ligand_count
        ligand_ratio_nowater = division_zero_div_handling(hetatm_count_nowater, ligand_count_nowater)
        try:
            asym_ids_with_metal = [i[0] for i in set(
                zip(self.mmcif_dict['_atom_site.label_asym_id'], self.mmcif_dict['_atom_site.type_symbol']))
                                   if i[1].lower() in METALS]
            hetatm_count_metal = len(
                [i for i in self.mmcif_dict['_atom_site.label_asym_id'] if i in asym_ids_with_metal])
            ligand_count_metal = len(asym_ids_with_metal)
        except KeyError:
            ligand_count_metal = NAN_VALUE
            hetatm_count_metal = NAN_VALUE
            print(self.key_error_output('asym ids with metal'))
        ligand_ratio_metal = division_zero_div_handling(hetatm_count_metal, ligand_count_metal)
        hetatm_count_nometal = subtraction_nan_handling(hetatm_count, hetatm_count_metal)
        ligand_count_nometal = subtraction_nan_handling(ligand_count, ligand_count_metal)
        ligand_ratio_nometal = division_zero_div_handling(hetatm_count_nometal, ligand_count_nometal)
        hetatm_count_nowater_nometal = subtraction_nan_handling(hetatm_count_nowater, hetatm_count_metal)
        ligand_count_nowater_nometal = subtraction_nan_handling(ligand_count_nowater, ligand_count_metal)
        ligand_ratio_nowater_nometal = division_zero_div_handling(hetatm_count_nowater_nometal,
                                                                  ligand_count_nowater_nometal)

        self.result_dict.update({'atomCount': atom_count, 'hetatmCount': hetatm_count, 'allAtomCount': all_atom_count,
                                 'allAtomCountLn': all_atom_count_ln, 'aaCount': aa_count, 'ligandCount': ligand_count,
                                 'aaLigandCount': aa_ligand_count, 'aaLigandCountNowater': aa_ligand_count_nowater,
                                 'ligandRatio': ligand_ratio, 'hetatmCountNowater': hetatm_count_nowater,
                                 'ligandCountNowater': ligand_count_nowater, 'ligandRatioNowater': ligand_ratio_nowater,
                                 'hetatmCountMetal': hetatm_count_metal, 'ligandCountMetal': ligand_count_metal,
                                 'ligandRatioMetal': ligand_ratio_metal, 'hetatmCountNometal': hetatm_count_nometal,
                                 'ligandCountNometal': ligand_count_nometal, 'ligandRatioNometal': ligand_ratio_nometal,
                                 'hetatmCountNowaterNometal': hetatm_count_nowater_nometal,
                                 'ligandCountNowaterNometal': ligand_count_nowater_nometal,
                                 'ligandRatioNowaterNometal': ligand_ratio_nowater_nometal})

    def create_result_dict(self):
        if super().file_exists():
            self.get_pdb_id()
            self.get_mmcif_resolution()
            self.get_pdb_release_date()
            self.get_structure_counts()
            self.get_structure_weights()
