from src.global_constants_and_functions import addition_nan_handling, key_error_output


class CombinedDataComputer:
    """
    computes factors that needs data from multiple files
    """

    def __init__(self, pdb_values_dict, vdb_values_dict):
        self.pdb_values_dict = pdb_values_dict
        self.vdb_values_dict = vdb_values_dict
        self.result_dict = {'aaLigandCountFiltered': 'nan'}
        self.get_counts()

    def get_counts(self):
        """
        get filtered values that need values from vdb and pdb/mmcif files
        :return: dict of values
        """
        if self.vdb_values_dict and self.pdb_values_dict:
            try:
                aa_ligand_count_filtered = addition_nan_handling(self.vdb_values_dict['ligandCountFiltered'] +
                                                                 self.pdb_values_dict['aaCount'])
                self.result_dict.update({'aaLigandCountFiltered': aa_ligand_count_filtered})
            except KeyError:
                print(key_error_output(self.pdb_values_dict['PDBID'], 'aa ligand count filtered (pdb + vdb)'))
