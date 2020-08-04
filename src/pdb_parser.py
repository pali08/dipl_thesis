import numpy as np
from Bio.File import as_handle
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from src.global_constants_and_functions import METALS, WATER_MOLECULE, division_zero_div_handling, to_float, to_int
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
        self.result_dict = {'PDBID': 'nan', 'releaseDate': 'nan', 'structureWeight': 'nan', 'polymerWeight': 'nan',
                            'nonPolymerWeight': 'nan',
                            'nonPolymerWeightNowater': 'nan', 'waterWeight': 'nan', 'atomCount': 'nan',
                            'hetatmCount': 'nan', 'allAtomCount': 'nan',
                            'allAtomCountLn': 'nan', 'aaCount': 'nan', 'ligandCount': 'nan',
                            'aaLigandCount': 'nan', 'aaLigandCountNowater': 'nan',
                            'ligandRatio': 'nan', 'hetatmCountNowater': 'nan',
                            'ligandCountNowater': 'nan', 'ligandRatioNowater': 'nan',
                            'hetatmCountMetal': 'nan', 'ligandCountMetal': 'nan',
                            'ligandRatioMetal': 'nan', 'hetatmCountNometal': 'nan',
                            'ligandCountNometal': 'nan', 'ligandRatioNometal': 'nan',
                            'hetatmCountNowaterNometal': 'nan',
                            'ligandCountNowaterNometal': 'nan',
                            'ligandRatioNowaterNometal': 'nan'}
        self.create_result_dict()

    def get_pdb_id(self):
        self.result_dict.update({'PDBID': self.mmcif_dict['_entry.id'][0]})

    def get_pdb_release_date(self):
        self.result_dict.update({'releaseDate': to_int(self.mmcif_dict['_citation.year'][0])})

    def get_structure_weights(self):
        """
        Get different structure weights based on type of molecules
        :return: list of weights
        """
        entities_list = list(zip(self.mmcif_dict['_entity.type'],
                                 [float(i[0]) * float(i[1]) for i in list(zip(self.mmcif_dict['_entity.formula_weight'],
                                                                              self.mmcif_dict[
                                                                                  '_entity.pdbx_number_of_molecules'
                                                                              ]))]))
        polymer_weight = float(sum([i[1] for i in entities_list if i[0] == "polymer"])) / 1000  # in kDaltons
        non_polymer_weight = float(sum([i[1] for i in entities_list if i[0] == "non-polymer"]))  # in Daltons
        water_weight = float(sum([i[1] for i in entities_list if i[0] == "water"]))  # in Daltons
        non_polymer_weight_with_water = non_polymer_weight + water_weight
        structure_weight = polymer_weight + (
                non_polymer_weight + water_weight) / 1000  # in kDaltons
        self.result_dict.update({'structureWeight': structure_weight, 'polymerWeight': polymer_weight,
                                 'nonPolymerWeight': non_polymer_weight_with_water,
                                 'nonPolymerWeightNowater': non_polymer_weight, 'waterWeight': water_weight})

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
            self.result_dict.update({'resolution': 'nan'})

    def get_structure_counts(self):
        """
        counts of atoms and ligands
        :return:
        """
        atom_count = len([i for i in self.mmcif_dict['_atom_site.group_PDB'] if i.upper() == 'ATOM'])
        hetatm_count = len([i for i in self.mmcif_dict['_atom_site.group_PDB'] if i.upper() == 'HETATM'])
        all_atom_count = atom_count + hetatm_count
        all_atom_count_ln = np.log(all_atom_count)
        aa_count = len(self.mmcif_dict['_entity_poly_seq.entity_id'])
        ligand_count = len(set([self.mmcif_dict['_atom_site.auth_seq_id'][i] for i in
                                range(0, len(self.mmcif_dict['_atom_site.auth_seq_id'])) if
                                self.mmcif_dict['_atom_site.group_PDB'][i].upper() == 'HETATM']))
        aa_ligand_count = aa_count + ligand_count
        nonwater_ligand_count = len(set([self.mmcif_dict['_atom_site.auth_seq_id'][i] for i in
                                         range(0, len(self.mmcif_dict['_atom_site.auth_seq_id'])) if
                                         self.mmcif_dict['_atom_site.group_PDB'][i].upper() == 'HETATM' and
                                         self.mmcif_dict['_atom_site.label_comp_id'][i].upper() != WATER_MOLECULE]))
        aa_ligand_count_nowater = aa_count + nonwater_ligand_count
        ligand_ratio = division_zero_div_handling(hetatm_count, ligand_count)
        hetatm_count_nowater = hetatm_count - len(
            [i for i in self.mmcif_dict['_atom_site.label_comp_id'] if i.upper() == WATER_MOLECULE])
        ligand_count_nowater = nonwater_ligand_count
        ligand_ratio_nowater = division_zero_div_handling(hetatm_count_nowater, ligand_count_nowater)
        asym_ids_with_metal = [i[0] for i in set(
            zip(self.mmcif_dict['_atom_site.label_asym_id'], self.mmcif_dict['_atom_site.type_symbol']))
                               if i[1].lower() in METALS]
        hetatm_count_metal = len([i for i in self.mmcif_dict['_atom_site.label_asym_id'] if i in asym_ids_with_metal])
        ligand_count_metal = len(asym_ids_with_metal)
        ligand_ratio_metal = division_zero_div_handling(hetatm_count_metal, ligand_count_metal)
        hetatm_count_nometal = hetatm_count - hetatm_count_metal
        ligand_count_nometal = ligand_count - ligand_count_metal
        ligand_ratio_nometal = division_zero_div_handling(hetatm_count_nometal, ligand_count_nometal)
        hetatm_count_nowater_nometal = hetatm_count_nowater - hetatm_count_metal
        ligand_count_nowater_nometal = ligand_count_nowater - ligand_count_metal
        ligand_ratio_nowater_nometal = division_zero_div_handling(hetatm_count_nowater_nometal,
                                                                  ligand_count_nowater_nometal)

        self.mmcif_dict.update({'atomCount': atom_count, 'hetatmCount': hetatm_count, 'allAtomCount': all_atom_count,
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
