import numpy as np
from Bio.File import as_handle
from Bio.PDB.MMCIF2Dict import MMCIF2Dict

from src.global_constants import metals, water_molecule


def get_mmcif_dictionary(filename):
    def get_mmcif_dictionary_local_function(fnm):
        return MMCIF2Dict(fnm)

    try:
        return get_mmcif_dictionary_local_function(filename)
    except UnicodeDecodeError:
        with as_handle(filename, 'r', encoding='utf-16') as f:
            return get_mmcif_dictionary_local_function(f)


class PdbParser:

    def __init__(self, filename):
        self.mmcif_dict = get_mmcif_dictionary(filename)

    def get_pdb_id(self):
        return self.mmcif_dict['_entry.id'][0]

    def get_pdb_release_date(self):
        return self.mmcif_dict['_citation.year'][0]

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
        return polymer_weight, non_polymer_weight, water_weight, non_polymer_weight_with_water, structure_weight

    def get_mmcif_resolution(self):
        """
        MMCIF is loaded as dictionary
        :param self.mmcif_dict
        :return: Highest resolution value if exists, nan otherwise.
        Highest resolution can be different item in different file. 2 of possibilities are covered for now
        """
        if '_refine.ls_d_res_high' in self.mmcif_dict:
            return self.mmcif_dict['_refine.ls_d_res_high'][0]
        return 'nan'

    def get_structure_counts(self):
        """
        counts of atoms and ligands
        :return:
        """
        atom_count = len([i for i in self.mmcif_dict['_atom_site.group_PDB'] if i.upper() == 'ATOM'])
        hetatm_count = len([i for i in self.mmcif_dict['_atom_site.group_PDB'] if i.upper() == 'HETATM'])
        all_atom_count = atom_count + hetatm_count
        all_atom_count_ln = np.log(all_atom_count)

        aa_count = len(self.mmcif_dict['_pdbx_poly_seq_scheme.pdb_mon_id'])
        ligand_count = len(self.mmcif_dict['_pdbx_nonpoly_scheme.mon_id'])
        # TODO (vdb parsing):
        ligand_bond_rotation_freedom = 'nan'
        aa_ligand_count = aa_count + ligand_count
        aa_ligand_count_nowater = aa_count + len(
            [i for i in self.mmcif_dict['_pdbx_nonpoly_scheme.mon_id'] if i.upper() != water_molecule])
        # TODO (vdb parsing)
        aa_ligand_count_filtered = 'nan'
        ligand_ratio = hetatm_count / ligand_count
        hetatm_count_nowater = hetatm_count - len(
            [i for i in self.mmcif_dict['_atom_site.label_comp_id'] if i.upper() == water_molecule])
        ligand_count_nowater = ligand_count - len(
            [i for i in self.mmcif_dict['_pdbx_nonpoly_scheme.mon_id'] if i.upper() == water_molecule])
        ligand_ratio_nowater = hetatm_count_nowater / ligand_count_nowater
        # TODO (vdbparsing):
        hetatm_count_filtered = 'nan'
        ligand_carbon_chiral_atom_count_filtered = 'nan'
        ligand_count_filtered = 'nan'
        ligand_ratio_filtered = 'nan'
        asym_ids_with_metal = [i[0] for i in set(
            zip(self.mmcif_dict['_atom_site.label_asym_id'], self.mmcif_dict['_atom_site.type_symbol']))
                               if i[1].lower() in metals]
        hetatm_count_metal = len([i for i in self.mmcif_dict['_atom_site.label_asym_id'] if i in asym_ids_with_metal])
        ligand_count_metal = len(asym_ids_with_metal)
        ligand_ratio_metal = hetatm_count_metal / ligand_count_metal
        hetatm_count_nometal = hetatm_count - hetatm_count_metal
        ligand_count_nometal = ligand_count - ligand_count_metal
        ligand_ratio_nometal = hetatm_count_nometal / ligand_count_nometal
        hetatm_count_nowater_nometal = hetatm_count_nowater - hetatm_count_metal
        ligand_count_nowater_nometal = ligand_count_nowater - ligand_count_metal
        ligand_ratio_nowater_nometal = hetatm_count_nowater_nometal / ligand_count_nowater_nometal
        # TODO (vdbparsing):
        hetatm_count_filtered_metal = 'nan'
        ligand_count_filtered_metal = 'nan'
        ligand_ratio_filtered_metal = 'nan'
        hetatm_count_filtered_nometal = 'nan'
        ligand_count_filtered_nometal = 'nan'
        ligand_ratio_filtered_nometal = 'nan'
        return atom_count, hetatm_count, all_atom_count, all_atom_count_ln, aa_count, ligand_count, aa_ligand_count, \
            aa_ligand_count_nowater, ligand_ratio, hetatm_count_nowater, ligand_count_nowater, ligand_ratio_nowater, \
            hetatm_count_metal, ligand_count_metal, ligand_ratio_metal, hetatm_count_nometal, ligand_count_nometal, \
            ligand_ratio_nometal, hetatm_count_nowater_nometal, ligand_count_nowater_nometal, \
            ligand_ratio_nowater_nometal
