import os
import csv
from src.global_constants_and_functions import NAN_VALUE, value_for_result_dictionary, BIOPOLYMERS
from src.json_parser import JsonParser


class UnknownSubfolderException(Exception):
    pass


class RestParser(JsonParser):
    # ligand_stats is static variable - when creating first RestParser object it is initialized
    # None -> dictionary.  When creating second, third... instances of the class, ligand stats dictionary
    # is already initialized - no need to initialize it again - it is same for all instances
    def __init__(self, filename, ligand_stats):
        super().__init__(filename)
        self.ligand_stats = ligand_stats
        print(filename)
        self.subfolder = filename.split(os.sep)[-2]
        self.molecule_name = filename.split(os.sep)[-1].split('.')[0].lower()
        self.all_values_list = self.json_dict[self.molecule_name]
        if self.subfolder.lower() == 'assembly':
            self.biopolymers_entities_list = NAN_VALUE
            self.ligand_entities_list = NAN_VALUE
            self.water_entities_list = NAN_VALUE
            self.ligand_entities_ids_list = NAN_VALUE
            self.result_dict = {'AssemblyTotalWeight': NAN_VALUE,
                                'AssemblyBiopolymerCount': NAN_VALUE,
                                'AssemblyUniqueBiopolymerCount': NAN_VALUE,
                                'AssemblyLigandCount': NAN_VALUE,
                                'AssemblyUniqueLigandCount': NAN_VALUE,
                                'AssemblyWaterCount': NAN_VALUE}
            if super().file_exists():
                self.get_assembly_data()
        elif self.subfolder.lower() == 'molecules':
            self.ligand_flexibility_raw = NAN_VALUE
            self.result_dict = {}
            if super().file_exists():
                self.get_molecules_data()
        elif self.subfolder.lower() == 'summary':
            self.result_dict = {'releaseDate': NAN_VALUE}
            self.get_summary_data()
            if super().file_exists():
                self.get_summary_data()
        else:
            raise UnknownSubfolderException(
                'Unknown subfolder name' + filename + 'names of subfolders in rest folders shoud be assembly, '
                                                      'molecules and summary')

    def get_assembly_data(self):
        molecular_weight = value_for_result_dictionary(self.all_values_list[0], 'molecular_weight')
        biopolymers_entities_list = [float(self.all_values_list[0]['entities'][i]['number_of_copies']) for i in
                                     range(0, len(self.all_values_list[0]['entities'])) if
                                     self.all_values_list[0]['entities'][i]['molecule_type'] in BIOPOLYMERS]
        self.biopolymers_entities_list = biopolymers_entities_list
        total_biopolymer_count = sum(biopolymers_entities_list)
        assembly_unique_biopolymer_count = len(biopolymers_entities_list)
        ligand_entities_list = [float(self.all_values_list[0]['entities'][i]['number_of_copies']) for i in
                                range(0, len(self.all_values_list[0]['entities'])) if
                                self.all_values_list[0]['entities'][i]['molecule_type'].lower() == 'bound']
        ligand_entity_ids_list = [self.all_values_list[0]['entities'][i]['entity_id'] for i in
                                  range(0, len(self.all_values_list[0]['entities'])) if
                                  self.all_values_list[0]['entities'][i]['molecule_type'].lower() == 'bound']
        self.ligand_entities_list = ligand_entities_list
        self.ligand_entities_ids_list = ligand_entity_ids_list
        total_ligand_count = sum(ligand_entities_list)
        ligand_entity_count = len(ligand_entities_list)
        water_entities_list = [float(self.all_values_list[0]['entities'][i]['number_of_copies']) for i in
                               range(0, len(self.all_values_list[0]['entities'])) if
                               self.all_values_list[0]['entities'][i]['molecule_type'].lower() == 'water']
        self.water_entities_list = water_entities_list
        total_water_count = sum(water_entities_list)
        self.result_dict.update(
            {'AssemblyTotalWeight': molecular_weight, 'AssemblyBiopolymerCount': total_biopolymer_count,
             'AssemblyUniqueBiopolymerCount': assembly_unique_biopolymer_count,
             'AssemblyLigandCount': total_ligand_count, 'AssemblyUniqueLigandCount': ligand_entity_count,
             'AssemblyWaterCount': total_water_count})

    def get_molecules_data(self):
        chem_comp_ids_num_of_copies_pairs = [
            [self.all_values_list[i]['chem_comp_ids'], self.all_values_list[i]['number_of_copies']] for i in
            range(0, len(self.all_values_list)) if
            'chem_comp_ids' in self.all_values_list[i] and 'molecule_type' in self.all_values_list[i] and
            self.all_values_list[i]['molecule_type'].lower() == 'bound']
        ligand_flexibility_raw = sum(
            [float(i[1]) * float(self.ligand_stats[j][1]) for i in chem_comp_ids_num_of_copies_pairs for j in i[0]
             if
             j.upper() in self.ligand_stats])
        self.ligand_flexibility_raw = ligand_flexibility_raw

    def get_summary_data(self):
        release_date = value_for_result_dictionary(self.json_dict[self.filename][0], 'release_date')
        self.result_dict.update({'releaseDate': release_date})
