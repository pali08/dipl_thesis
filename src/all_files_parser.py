import os

from src.global_constants_and_functions import is_float
from src.pdb_parser import PdbParser
from src.combined_data_computer import CombinedDataComputer
from src.vdb_parser import VdbParser


class AllFilesParser:

    def __init__(self, molecule, *filepaths):
        self.filepaths = filepaths
        self.molecule = molecule
        self.pdb_dict = PdbParser(self.get_pdb_filepath()).result_dict
        self.vdb_dict = VdbParser(self.get_vdb_filepath()).result_dict
        self.pdb_vdb_dict = CombinedDataComputer(self.pdb_dict, self.vdb_dict).result_dict
        self.result_dict = {**self.pdb_dict, **self.vdb_dict, **self.pdb_vdb_dict}

    order_list = ['PDB ID', 'resolution', 'releaseDate', 'StructureWeight', 'PolymerWeight',
                  'NonpolymerWeight',
                  'NonpolymerWeightNowater',
                  'WaterWeight', 'atomCount', 'hetatmCount', 'allAtomCount', 'allAtomCountLn', 'aaCount',
                  'ligandCount',
                  'ligandBondRotationFreedom', 'aaLigandCount', 'aaLigandCountNowater',
                  'aaLigandCountFiltered',
                  'ligandRatio', 'hetatmCountNowater', 'ligandCountNowater', 'ligandRatioNowater',
                  'hetatmCountFiltered', 'ligandCarbonChiraAtomCountFiltered', 'ligandCountFiltered',
                  'ligandRatioFiltered', 'hetatmCountMetal', 'ligandCountMetal', 'ligandRatioMetal',
                  'hetatmCountNometal', 'ligandCountNometal', 'ligandRatioNometal',
                  'hetatmCountNowaterNometal', 'ligandCountNowaterNometal', 'ligandRatioNowaterNometal',
                  'hetatmCountFilteredMetal', 'ligandCountFilteredMetal', 'ligandRatioFilteredMetal',
                  'hetatmCountFilteredNometal', 'ligandCountFilteredNometal', 'ligandRatioFilteredNometal']

    def get_data_ordered(self):
        """
        order result data in original data.csv format
        :return:
        """
        ordered_list = []
        for i in AllFilesParser.order_list:
            ordered_list.append(self.result_dict[i])
        return ordered_list

    def get_pdb_filepath(self):
        # print(self.molecule)
        # print(self.filepaths[0])
        return os.path.join(self.filepaths[0], self.molecule + '_updated.cif')

    def get_vdb_filepath(self):
        return os.path.join(self.filepaths[1], self.molecule, 'result.json')

    def get_xml_filepath(self):
        pass
        # TODO return os.path.join(self.filepaths[2], self.molecule + '_validation.xml')

    def get_rest_filepath(self, subfolder):
        pass
        # TODO return os.path.join(self.filepaths[3], subfolder, self.molecule + '.json')

    def result_dict_final_edit(self):
        """
        format floating point numbers to 3 decimals
        :return:
        """
        for key, value in self.result_dict:
            if '.' in value:
                self.result_dict[key] = '{:.3f}'.format(float(value))

