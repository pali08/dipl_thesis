import numpy as np
from Bio.File import as_handle
from Bio.PDB.MMCIF2Dict import MMCIF2Dict


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
        atom_count = len([i for i in self.mmcif_dict if i.upper() == 'ATOM'])
        hetatm_count = len([i for i in self.mmcif_dict if i.upper() == 'HETATM'])
        all_atom_count = atom_count + hetatm_count
        all_atom_count_ln = np.log(all_atom_count)

        aa_count = len(self.mmcif_dict['_pdbx_poly_seq_scheme.pdb_mon_id'])
        ligand_count = len(self.mmcif_dict['_pdbx_nonpoly_scheme.mon_id'])
        # TODO: ligand_bond_rotation_freedom = 'nan'
        aa_ligand_count = aa_count + ligand_count
        aa_ligand_count_nowater = aa_count + len(
            [i for i in self.mmcif_dict['_pdbx_nonpoly_scheme.mon_id'] if i.upper() != 'HOH'])
