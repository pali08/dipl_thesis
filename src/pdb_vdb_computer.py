from src.global_constants_and_functions import addition_nan_handling


class PdbVdbComputer:
    """
    computes factors that needs data from pdb and vdb files
    """

    def __init__(self, pdb_values_dict, vdb_values_dict):
        self.pdb_values_dict = pdb_values_dict
        self.vdb_values_dict = vdb_values_dict

    def get_counts_filtered(self):
        """
        get filtered values that need values from vdb and pdb/mmcif files
        :return: dict of values
        """
        aa_ligand_count_filtered = addition_nan_handling(self.vdb_values_dict['ligand_count_filtered'] +
                                                         self.pdb_values_dict['aa_count'])


