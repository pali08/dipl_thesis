from src.global_constants_and_functions import addition_nan_handling, key_error_output, NAN_VALUE, \
    division_zero_div_handling, check_dictionary_contains_only_nan_values, BIOPOLYMERS, value_for_result_dictionary


class CombinedDataComputer:
    """
    computes factors that needs data from multiple files
    """

    def __init__(self, pdb_values_dict, vdb_values_dict, xml_values_dict, rest_assembly_values_dict,
                 rest_molecules_values_dict, rest_summary_values_dict, rest_assembly_parser, rest_molecules_parser,
                 rest_summary_parser, ligand_stats):
        self.pdb_values_dict = pdb_values_dict
        self.vdb_values_dict = vdb_values_dict
        self.xml_values_dict = xml_values_dict
        self.rest_assembly_values_dict = rest_assembly_values_dict
        self.rest_molecules_values_dict = rest_molecules_values_dict
        self.rest_summary_values_dict = rest_summary_values_dict
        self.rest_assembly_parser = rest_assembly_parser
        self.rest_molecules_parser = rest_molecules_parser
        self.rest_summary_parser = rest_summary_parser
        self.ligand_entities_list = NAN_VALUE
        self.ligand_stats = ligand_stats
        self.result_dict = {'aaLigandCountFiltered': NAN_VALUE, 'combinedOverallQualityMetric': NAN_VALUE,
                            'AssemblyBiopolymerWeight': NAN_VALUE, 'AssemblyLigandWeight': NAN_VALUE,
                            'AssemblyWaterWeight': NAN_VALUE, 'AssemblyLigandFlexibility': NAN_VALUE,
                            'AssemblyTotalWeight': NAN_VALUE,
                            'AssemblyBiopolymerCount': NAN_VALUE,
                            'AssemblyUniqueBiopolymerCount': NAN_VALUE,
                            'AssemblyLigandCount': NAN_VALUE,
                            'AssemblyUniqueLigandCount': NAN_VALUE,
                            'AssemblyWaterCount': NAN_VALUE}
        self.get_data()

    def get_data(self):
        """
        get filtered values that need values from vdb and pdb/mmcif files
        :return: dict of values
        """
        if not check_dictionary_contains_only_nan_values(self.vdb_values_dict) and \
                not check_dictionary_contains_only_nan_values(self.pdb_values_dict):
            try:
                aa_ligand_count_filtered = addition_nan_handling(self.vdb_values_dict['ligandCountFiltered'] +
                                                                 self.pdb_values_dict['aaCount'])
                self.result_dict.update({'aaLigandCountFiltered': aa_ligand_count_filtered})
            except KeyError:
                print(key_error_output(self.pdb_values_dict['PDBID'], 'aa ligand count filtered (pdb + vdb)'))
        if self.xml_values_dict['combinedGeometryQuality'] != NAN_VALUE and \
                self.xml_values_dict['combinedXrayQualityMetric'] != NAN_VALUE and \
                self.pdb_values_dict['resolution'] != NAN_VALUE:
            self.result_dict.update({'combinedOverallQualityMetric': (self.xml_values_dict['combinedGeometryQuality'] +
                                                                      self.xml_values_dict[
                                                                          'combinedXrayQualityMetric'] - 30 *
                                                                      self.pdb_values_dict['resolution']) / 2})
        if not check_dictionary_contains_only_nan_values(
                self.rest_molecules_values_dict) and not check_dictionary_contains_only_nan_values(
            self.rest_summary_values_dict):
            key_of_preferred_assembly = [index for index, i in enumerate(self.rest_assembly_parser.all_values_list) if
                                         i['assembly_id'] == self.rest_summary_parser.prefered_assembly_id][0]
            preferred_assembly = self.rest_assembly_parser.all_values_list[key_of_preferred_assembly]

            molecular_weight = value_for_result_dictionary(preferred_assembly,
                                                           'molecular_weight')  # / self.polymeric_count
            biopolymers_entities_list = [float(preferred_assembly['entities'][i]['number_of_copies']) for i in
                                         range(0, len(preferred_assembly['entities'])) if
                                         preferred_assembly['entities'][i]['molecule_type'] in BIOPOLYMERS]
            total_biopolymer_count = sum(biopolymers_entities_list)  # / self.polymeric_count
            assembly_unique_biopolymer_count = len(biopolymers_entities_list)
            ligand_entities_list = [float(preferred_assembly['entities'][i]['number_of_copies']) for i in
                                    range(0, len(preferred_assembly['entities'])) if
                                    preferred_assembly['entities'][i]['molecule_type'].lower() == 'bound']
            self.ligand_entities_list = ligand_entities_list
            total_ligand_count = sum(ligand_entities_list)  # / self.polymeric_count
            ligand_entity_count = len(ligand_entities_list)
            water_entities_list = [float(preferred_assembly['entities'][i]['number_of_copies']) for i in
                                   range(0, len(preferred_assembly['entities'])) if
                                   preferred_assembly['entities'][i]['molecule_type'].lower() == 'water']
            total_water_count = sum(water_entities_list)  # / self.polymeric_count
            self.result_dict.update(
                {'AssemblyTotalWeight': molecular_weight, 'AssemblyBiopolymerCount': total_biopolymer_count,
                 'AssemblyUniqueBiopolymerCount': assembly_unique_biopolymer_count,
                 'AssemblyLigandCount': total_ligand_count, 'AssemblyUniqueLigandCount': ligand_entity_count,
                 'AssemblyWaterCount': total_water_count})
            total_biopolymer_weight = (sum(
                [j['weight'] * i['number_of_copies'] for j in self.rest_molecules_parser.all_values_list for i in
                 preferred_assembly['entities'] if
                 i['entity_id'] == j['entity_id'] and j['molecule_type'] in BIOPOLYMERS and j[
                     'weight'] is not None and i[
                     'number_of_copies'] is not None]) / 1000)  # / self.rest_assembly_parser.polymeric_count
            total_ligand_weight = sum(
                [j['weight'] * i['number_of_copies'] for j in self.rest_molecules_parser.all_values_list for i in
                 preferred_assembly['entities'] if
                 i['entity_id'] == j['entity_id'] and j['molecule_type'].lower() == 'bound' and j[
                     'weight'] is not None and i[
                     'number_of_copies'] is not None])  # / self.rest_assembly_parser.polymeric_count
            total_water_weight = sum(
                [j['weight'] * i['number_of_copies'] for j in self.rest_molecules_parser.all_values_list for i in
                 preferred_assembly['entities'] if
                 i['entity_id'] == j['entity_id'] and 'water' in [k.lower() for k in j['molecule_name']] and j[
                     'weight'] is not None and i[
                     'number_of_copies'] is not None])  # / self.rest_assembly_parser.polymeric_count
            chem_comp_ids_num_of_copies_pairs = [[i['chem_comp_ids'], j['number_of_copies']] for i in
                                                 self.rest_molecules_parser.all_values_list for j in
                                                 preferred_assembly['entities'] if
                                                 'chem_comp_ids' in i and 'number_of_copies' in j and i['entity_id'] ==
                                                 j['entity_id'] and i['molecule_type'].lower() == 'bound']
            ligand_flexibility_raw = sum(
                [float(i[1]) * float(self.ligand_stats[j][1]) for i in chem_comp_ids_num_of_copies_pairs for j in i[0]
                 if
                 j.upper() in self.ligand_stats])
            assembly_ligand_flexibility = division_zero_div_handling(ligand_flexibility_raw, sum(ligand_entities_list))
            self.result_dict.update(
                {'AssemblyBiopolymerWeight': total_biopolymer_weight, 'AssemblyLigandWeight': total_ligand_weight,
                 'AssemblyWaterWeight': total_water_weight, 'AssemblyLigandFlexibility': assembly_ligand_flexibility})
