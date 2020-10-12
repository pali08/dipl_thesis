from src.global_constants_and_functions import addition_nan_handling, key_error_output, NAN_VALUE, \
    division_zero_div_handling


class CombinedDataComputer:
    """
    computes factors that needs data from multiple files
    """

    def __init__(self, pdb_values_dict, vdb_values_dict, xml_values_dict, rest_assembly_values_dict,
                 rest_molecules_values_dict, rest_summary_values_dict):
        self.pdb_values_dict = pdb_values_dict
        self.vdb_values_dict = vdb_values_dict
        self.xml_values_dict = xml_values_dict
        self.rest_assembly_values_dict = rest_assembly_values_dict
        self.rest_molecules_values_dict = rest_molecules_values_dict
        self.rest_summary_values_dict = rest_summary_values_dict
        self.result_dict = {'aaLigandCountFiltered': NAN_VALUE, 'combinedOverallQualityMetric': NAN_VALUE}
        self.get_data()

    def get_data(self):
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
        if self.xml_values_dict['combinedGeometryQuality'] != NAN_VALUE and self.xml_values_dict[
            'combinedXrayQualityMetric'] != NAN_VALUE and self.pdb_values_dict['resolution'] != NAN_VALUE:
            self.result_dict.update({'combinedOverallQualityMetric': (self.xml_values_dict['combinedGeometryQuality'] +
                                                                      self.xml_values_dict[
                                                                          'combinedXrayQualityMetric'] - 30 *
                                                                      self.pdb_values_dict['resolution']) / 2})
        if self.rest_assembly_values_dict and self.rest_molecules_values_dict:
            total_biopolymer_weight = sum(
                [self.rest_assembly_values_dict.biopolymers_entities_list[i] *
                 self.rest_molecules_values_dict.all_values_list[0]['weight'] for i in
                 range(0, len(self.rest_assembly_values_dict.biopolymers_entities_list))]) / 1000
            total_ligand_weight = sum(
                [self.rest_assembly_values_dict.ligand_entities_list[i] *
                 self.rest_molecules_values_dict.all_values_list[0]['weight'] for i in
                 range(0, len(self.rest_assembly_values_dict.ligand_entities_list))])
            total_water_weight = sum(
                [self.rest_assembly_values_dict.water_entities_list[i] *
                 self.rest_molecules_values_dict.all_values_list[0]['weight'] for i in
                 range(0, len(self.rest_assembly_values_dict.water_entities_list))])
            assembly_ligand_flexibility = division_zero_div_handling(
                sum(self.rest_assembly_values_dict.ligand_entities_list),
                self.rest_molecules_values_dict.ligand_flexibility_raw)
            self.result_dict.update(
                {'AssemblyBiopolymerWeight': total_biopolymer_weight, 'AssemblyLigandWeight': total_ligand_weight,
                 'AssemblyWaterWeight': total_water_weight, 'AssemblyLigandFlexibility': assembly_ligand_flexibility})
