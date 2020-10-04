import os

from src.global_constants_and_functions import NAN_VALUE, value_for_result_dictionary, biopolymers
from src.json_parser import JsonParser


class UnknownSubfolderException(Exception):
    pass


class RestParser(JsonParser):
    def __init__(self, filename):
        super().__init__(filename)
        self.subfolder = filename.split(os.linesep)[-2]
        self.molecule_name = filename.split(os.linesep)[-1].split('.')[0].lower()
        self.all_values_list = self.json_dict[self.molecule_name]
        if self.subfolder.lower() == 'assembly':
            self.biopolymers_entities_list = None
            self.result_dict = {}
            self.get_assembly_data()
        elif self.subfolder.lower() == 'molecules':
            self.result_dict = {}
            self.get_molecules_data()
        elif self.subfolder.lower() == 'summary':
            self.result_dict = {}
            self.get_summary_data()
        else:
            raise UnknownSubfolderException(
                'Unknown subfolder name' + filename + 'names of subfolders in rest folders shoud be assembly, '
                                                      'molecules and summary')

    def get_assembly_data(self):
        molecular_weight = value_for_result_dictionary(self.all_values_list[0], 'molecular_weight')
        biopolymers_entities_list = [float(self.all_values_list[0]['entities'][i]['number_of_copies']) for i in
                                     range(0, len(self.all_values_list[0]['entities'])) if
                                     self.all_values_list[0]['entities'][i]['molecule_type'] in biopolymers]
        self.biopolymers_entities_list = biopolymers_entities_list
        total_biopolymer_count = sum(biopolymers_entities_list)
        assembly_unique_biopolymer_count = len(biopolymers_entities_list)
        ligand_entities_list = [float(self.all_values_list[0]['entities'][i]['number_of_copies']) for i in
                                range(0, len(self.all_values_list[0]['entities'])) if
                                self.all_values_list[0]['entities'][i]['molecule_type'].lower() == 'bound']
        total_ligand_count = sum(ligand_entities_list)
        ligand_entity_count = len(ligand_entities_list)
        water_entities_list = [float(self.all_values_list[0]['entities'][i]['number_of_copies']) for i in
                               range(0, len(self.all_values_list[0]['entities'])) if
                               self.all_values_list[0]['entities'][i]['molecule_type'].lower() == 'water']
        total_water_count = sum(water_entities_list)
        self.result_dict.update(
            {'AssemblyTotalWeight': molecular_weight, 'AssemblyBiopolymerCount': total_biopolymer_count,
             'AssemblyUniqueBiopolymerCount': assembly_unique_biopolymer_count,
             'AssemblyLigandCount': total_ligand_count, 'AssemblyUniqueLigandCount': ligand_entity_count,
             'AssemblyWaterCount': total_water_count})

    def get_molecules_data(self):
        pass

    def get_summary_data(self):
        release_date = value_for_result_dictionary(self.json_dict[self.filename][0], 'release_date')

